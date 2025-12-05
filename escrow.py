#!/usr/bin/env python3
# escrow_bot_fixed.py
# Corrected single-file Escrow Bot — fixes:
# 1) Set Role option added to main menu
# 2) Cancel button standardized and fixed
# 3) Welcome uses HTML, bold, prettier
# 4) Welcome shows full name (fallback to user id)
# 5) Safe reply helper prevents NoneType.reply_text errors
# All other features (create flow, payments, approvals, PDF, etc.) preserved.

import os
import sqlite3
import hashlib
import secrets
import time
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- CONFIG ----------------
BOT_TOKEN = "8343440179:AAEKCVNQb1LS6igMY-yfjjI3QQpcdQ4PM9Y"  # your token
INITIAL_ADMIN_IDS = {6127646960}  # initial trusted admin IDs
DB_PATH = "escrow_bot.db"
ESCROW_FEE_PERCENT = 3.0
EXTRA_NO_BIO_FEE_PERCENT = 3.0
CANCEL_FEE_PERCENT = 3.0
PAGE_SIZE = 10
PAYMENT_DIR = "payments"
PDF_DIR = "pdfs"
os.makedirs(PAYMENT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# conversation states for create flow
(
    S_SELECT_BUYER, S_SELECT_SELLER, S_SELECT_ESCROWER,
    S_ENTER_AMOUNT, S_ENTER_CURRENCY, S_ENTER_DAYS, S_ENTER_DESC,
    S_CONFIRM
) = range(8)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- DB helpers ----------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        fullname TEXT,
        role TEXT DEFAULT 'buyer',
        verified INTEGER DEFAULT 0,
        bio_verified INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS pending_escrowers (
        id INTEGER PRIMARY KEY,
        username TEXT,
        requested_at TEXT,
        approved INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS deals (
        txid TEXT PRIMARY KEY,
        buyer_id INTEGER,
        seller_id INTEGER,
        admin_id INTEGER,
        amount REAL,
        currency TEXT,
        fee REAL,
        status TEXT,
        time_to_complete_days INTEGER,
        escrow_till TEXT,
        description TEXT,
        chat_id INTEGER,
        created_at TEXT,
        updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        txid TEXT,
        uploaded_by INTEGER,
        file_id TEXT,
        file_path TEXT,
        approved INTEGER DEFAULT 0,
        uploaded_at TEXT
    );
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        txid TEXT,
        actor_id INTEGER,
        action TEXT,
        note TEXT,
        ts TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS action_tokens (
        token TEXT PRIMARY KEY,
        txid TEXT,
        action TEXT,
        user_id INTEGER,
        expires_at TEXT
    );
    """)
    # ensure initial admins exist as escrower+verified
    for aid in INITIAL_ADMIN_IDS:
        cur.execute("INSERT OR IGNORE INTO users(id, username, role, verified, fullname) VALUES (?, ?, 'escrower', 1, ?)",
                    (aid, f"admin_{aid}", f"Admin {aid}"))
    conn.commit()
    conn.close()

# ---------------- Utils ----------------
def now_iso(): return datetime.utcnow().isoformat(sep=' ', timespec='seconds')
def escrow_till_iso(days): return (datetime.utcnow() + timedelta(days=days)).isoformat(sep=' ', timespec='seconds')

def register_user_if_missing(user):
    if not user:
        return
    conn = get_connection()
    cur = conn.cursor()
    fullname = " ".join(filter(None, [user.first_name, user.last_name])) if user else ""
    cur.execute("INSERT OR IGNORE INTO users(id, username, fullname, role, verified, created_at) VALUES (?, ?, ?, 'buyer', 0, ?)",
                (user.id, user.username or f"user{user.id}", fullname or None, now_iso()))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    r = cur.fetchone()
    conn.close()
    return r

def set_role(user_id, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users(id, username, role, verified, created_at) VALUES (?,?,?,0,?)",
                (user_id, f"user{user_id}", role, now_iso()))
    cur.execute("UPDATE users SET role=?, verified=0 WHERE id=?", (role, user_id))
    conn.commit()
    conn.close()

def require_verified(user_id: int, role: Optional[str]=None) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    if role:
        cur.execute("SELECT verified FROM users WHERE id=? AND role=?", (user_id, role))
    else:
        cur.execute("SELECT verified FROM users WHERE id=?", (user_id,))
    r = cur.fetchone()
    conn.close()
    return bool(r and r["verified"] == 1)

def fee_for_amount(amount, bio_verified=True):
    base = round(amount * (ESCROW_FEE_PERCENT / 100.0), 2)
    if not bio_verified:
        base += round(amount * (EXTRA_NO_BIO_FEE_PERCENT / 100.0), 2)
    return base

def generate_unique_txid(buyer_id, seller_id, admin_id):
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(10):
        raw = f"{buyer_id}|{seller_id}|{admin_id}|{time.time_ns()}|{secrets.token_hex(8)}"
        tx = hashlib.sha256(raw.encode()).hexdigest().upper()[:14]
        cur.execute("SELECT 1 FROM deals WHERE txid=?", (tx,))
        if not cur.fetchone():
            conn.close()
            return tx
    # fallback
    raw = f"{buyer_id}|{seller_id}|{admin_id}|{time.time_ns()}|{secrets.token_hex(32)}"
    tx = hashlib.sha256(raw.encode()).hexdigest().upper()
    conn.close()
    return tx

def add_log(txid, actor_id, action, note=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs(txid, actor_id, action, note, ts) VALUES (?,?,?,?,?)", (txid, actor_id, action, note, now_iso()))
    conn.commit()
    conn.close()

# ---------------- Safe reply helper ----------------
async def safe_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode: Optional[str]=None):
    """
    Reply safely whether update is a message, callback_query, or other.
    Uses edit_message_text for callback_query where possible.
    """
    try:
        if getattr(update, "callback_query", None) and update.callback_query is not None:
            q = update.callback_query
            try:
                await q.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
                return
            except Exception:
                # fallback to sending new message to chat
                chat_id = q.message.chat_id if q.message else q.from_user.id
                await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
                return
        if getattr(update, "message", None) and update.message is not None:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            return
        # fallback: send to user
        chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.exception("safe_reply failed: %s", e)

# ---------------- Inline UI elements ----------------
MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("💼 Create Deal", callback_data="menu:create")],
    [InlineKeyboardButton("📁 My Deals", callback_data="menu:mydeals"), InlineKeyboardButton("🧾 Get PDF", callback_data="menu:getpdf")],
    [InlineKeyboardButton("🔁 Set Role", callback_data="menu:setrole"), InlineKeyboardButton("📤 Upload Payment", callback_data="menu:upload")],
    [InlineKeyboardButton("🛡️ Request Verification", callback_data="menu:reqverify"), InlineKeyboardButton("🧑‍⚖️ Become Escrower", callback_data="menu:become_escrower")],
    [InlineKeyboardButton("ℹ️ Help", callback_data="menu:help")]
])
ROLE_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧾 Buyer", callback_data="role:buyer"), InlineKeyboardButton("🛍️ Seller", callback_data="role:seller")],
    [InlineKeyboardButton("🛡️ Escrower", callback_data="role:escrower"), InlineKeyboardButton("Skip", callback_data="role:skip")]
])
HELP_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("How to create a deal", callback_data="help:create")],
    [InlineKeyboardButton("Payment proof", callback_data="help:upload")],
    [InlineKeyboardButton("Fees & cancel", callback_data="help:fees")],
    [InlineKeyboardButton("Admin list", callback_data="help:admins")],
    [InlineKeyboardButton("Main menu", callback_data="menu:main")]
])

# ---------------- Commands and callbacks ----------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user_if_missing(user)
    row = get_user(user.id)
    verified = bool(row and row['verified'] == 1)
    # determine display name (first + last) fallback to id
    name = None
    if user:
        if user.first_name or user.last_name:
            name = " ".join(filter(None, [user.first_name, user.last_name]))
    if not name:
        name = str(user.id)
    # welcome HTML
    welcome = (
        f"<b>Welcome, {name}!</b>\n\n"
        "This is <b>Escrow Bot — Professional</b>.\n"
        "Use the inline menu below to perform actions. Pick your role if you haven't yet."
    )
    # prompt role selection if role missing or unverified buyer/seller
    role = row['role'] if row else None
    if not role or (role in ("buyer","seller") and not verified):
        await safe_reply(update, context, welcome + "\n\nChoose your role:", reply_markup=ROLE_KB, parse_mode="HTML")
        return
    # else show main menu
    await safe_reply(update, context, welcome + f"\n\nRole: <b>{role}</b> • Verified: {'✅' if verified else '❌'}", reply_markup=MAIN_MENU, parse_mode="HTML")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update, context, "Help & Topics", reply_markup=HELP_KB)

async def cb_role_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data.split(":",1)[1]
    user = q.from_user
    register_user_if_missing(user)
    if data == "skip":
        await safe_reply(update, context, "You can set your role later from the menu.", reply_markup=MAIN_MENU)
        return
    set_role(user.id, data)
    if data in ("buyer","seller"):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Request Verification", callback_data=f"reqverify:{user.id}")],
                                   [InlineKeyboardButton("Main Menu", callback_data="menu:main")]])
        await safe_reply(update, context, f"Role set to <b>{data}</b>. You are not verified yet. Request verification to access deals.", reply_markup=kb, parse_mode="HTML")
        # notify admins (optional)
        for aid in INITIAL_ADMIN_IDS:
            try:
                await context.bot.send_message(aid, f"User @{user.username or user.id} set role {data} (unverified).")
            except Exception:
                pass
    else:
        # escrower: submit pending escrower
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO pending_escrowers(id, username, requested_at) VALUES (?,?,?)",
                    (user.id, user.username or f"user{user.id}", now_iso()))
        conn.commit()
        conn.close()
        for aid in INITIAL_ADMIN_IDS:
            try:
                await context.bot.send_message(aid, f"User @{user.username or user.id} requested to become escrower.")
            except Exception:
                pass
        await safe_reply(update, context, "Escrower request submitted to admins.", reply_markup=MAIN_MENU)

async def cb_reqverify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 2:
        await safe_reply(update, context, "Invalid request.", reply_markup=MAIN_MENU)
        return
    uid = int(parts[1])
    row = get_user(uid)
    if not row:
        await safe_reply(update, context, "User not found.", reply_markup=MAIN_MENU)
        return
    # notify admins with approve button
    for aid in INITIAL_ADMIN_IDS:
        try:
            await context.bot.send_message(aid, f"Verification request: @{row['username']} (role: {row['role']}).",
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Approve", callback_data=f"verify_user:{uid}:approve")]]))
        except Exception:
            pass
    await safe_reply(update, context, "Verification request sent to admins.", reply_markup=MAIN_MENU)

async def cb_verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 3:
        await safe_reply(update, context, "Invalid.", reply_markup=MAIN_MENU)
        return
    uid = int(parts[1]); action = parts[2]
    actor = q.from_user
    if actor.id not in INITIAL_ADMIN_IDS and not require_verified(actor.id, 'escrower'):
        await safe_reply(update, context, "Not authorized.", reply_markup=MAIN_MENU)
        return
    if action != "approve":
        await safe_reply(update, context, "Unsupported action.", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET verified=1 WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    try:
        await context.bot.send_message(uid, f"✅ You were verified by admin @{actor.username or actor.id}.")
    except Exception:
        pass
    await safe_reply(update, context, f"User {uid} verified.", reply_markup=MAIN_MENU)

# pending escrower flow
async def cmd_pending_escrowers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in INITIAL_ADMIN_IDS and not require_verified(user.id, 'escrower'):
        await safe_reply(update, context, "Not authorized.", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM pending_escrowers WHERE approved=0")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await safe_reply(update, context, "No pending escrower requests.", reply_markup=MAIN_MENU)
        return
    kb = [[InlineKeyboardButton(f"{r['username']} (id:{r['id']})", callback_data=f"esc_approve:{r['id']}")] for r in rows]
    await safe_reply(update, context, "Pending escrowers:", reply_markup=InlineKeyboardMarkup(kb))

async def cb_esc_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 2:
        await safe_reply(update, context, "Invalid.", reply_markup=MAIN_MENU)
        return
    uid = int(parts[1])
    actor = q.from_user
    if actor.id not in INITIAL_ADMIN_IDS and not require_verified(actor.id, 'escrower'):
        await safe_reply(update, context, "Not authorized.", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM pending_escrowers WHERE id=? AND approved=0", (uid,))
    r = cur.fetchone()
    if not r:
        conn.close()
        await safe_reply(update, context, "Request not found or processed.", reply_markup=MAIN_MENU)
        return
    cur.execute("UPDATE pending_escrowers SET approved=1 WHERE id=?", (uid,))
    cur.execute("INSERT OR IGNORE INTO users(id, username, role, verified) VALUES (?,?, 'escrower', 1)", (uid, r['username']))
    cur.execute("UPDATE users SET role='escrower', verified=1 WHERE id=?", (uid,))
    conn.commit()
    conn.close()
    await safe_reply(update, context, f"Approved {r['username']} as escrower.", reply_markup=MAIN_MENU)

# helper fetch role rows
def fetch_role_rows(role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role=? AND verified=1 ORDER BY username", (role,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ------------- Create flow (strict conversation) --------------
async def create_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # entry either command or callback
    user = update.effective_user
    register_user_if_missing(user)
    if not require_verified(user.id):
        await safe_reply(update, context, "❌ Only verified users may create deals. Request verification.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    context.user_data['create'] = {'data': {}, 'pages': {'buyer':0,'seller':0,'escrower':0}, 'chat_id': update.effective_chat.id if update.effective_chat else None}
    return await send_role_selection(update, context, role='buyer', page=0)

async def send_role_selection(update_or_q, context, role='buyer', page=0):
    rows = fetch_role_rows(role)
    if not rows:
        await safe_reply(update_or_q, context, f"No verified {role}s available. Ask admins to verify users.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    start = page * PAGE_SIZE
    page_rows = rows[start:start+PAGE_SIZE]
    kb = []
    for r in page_rows:
        kb.append([InlineKeyboardButton(f"{r['username']} ({r['id']})", callback_data=f"pick:{role}:{r['id']}")])
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"nav:{role}:{page-1}"))
    if start + PAGE_SIZE < len(rows):
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"nav:{role}:{page+1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("Cancel", callback_data="create:cancel")])
    text = f"Select {role.capitalize()} (page {page+1}):"
    await safe_reply(update_or_q, context, text, reply_markup=InlineKeyboardMarkup(kb))
    return {'buyer': S_SELECT_BUYER, 'seller': S_SELECT_SELLER, 'escrower': S_SELECT_ESCROWER}[role]

async def cb_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, role, page_s = q.data.split(":")
    page = int(page_s)
    create = context.user_data.get('create', {'pages': {}})
    create['pages'][role] = page
    context.user_data['create'] = create
    await send_role_selection(q, context, role=role, page=page)

async def cb_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 3:
        await safe_reply(q, context, "Invalid selection.", reply_markup=MAIN_MENU)
        context.user_data.pop('create', None)
        return ConversationHandler.END
    _, role, id_s = parts
    uid = int(id_s)
    create = context.user_data.get('create')
    if not create:
        await safe_reply(q, context, "Session expired. Start /create again.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    create['data'][f"{role}_id"] = uid
    context.user_data['create'] = create
    add_log("N/A", q.from_user.id, f"PICK_{role.upper()}", f"picked {uid}")
    if role == 'buyer':
        return await send_role_selection(q, context, role='seller', page=0)
    if role == 'seller':
        return await send_role_selection(q, context, role='escrower', page=0)
    if role == 'escrower':
        await safe_reply(q, context, "Enter deal amount now (send as message, e.g., 250.00):")
        return S_ENTER_AMOUNT
    await safe_reply(q, context, "Unexpected role.", reply_markup=MAIN_MENU)
    context.user_data.pop('create', None)
    return ConversationHandler.END

# text states
async def create_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create = context.user_data.get('create')
    if not create:
        await safe_reply(update, context, "Session expired. Start again with /create.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    try:
        amt = float(update.message.text.strip())
        if amt <= 0:
            raise ValueError()
    except Exception:
        await safe_reply(update, context, "Invalid amount. Send numeric like 999.99")
        return S_ENTER_AMOUNT
    create['data']['amount'] = round(amt,2)
    context.user_data['create'] = create
    await safe_reply(update, context, "Enter currency code (e.g., USD, INR):")
    return S_ENTER_CURRENCY

async def create_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create = context.user_data.get('create')
    if not create:
        await safe_reply(update, context, "Session expired.")
        return ConversationHandler.END
    code = update.message.text.strip().upper()
    if not code.isalpha() or len(code) > 6:
        await safe_reply(update, context, "Invalid currency. Try USD or INR.")
        return S_ENTER_CURRENCY
    create['data']['currency'] = code
    context.user_data['create'] = create
    await safe_reply(update, context, "Enter time to complete (days, integer):")
    return S_ENTER_DAYS

async def create_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create = context.user_data.get('create')
    if not create:
        await safe_reply(update, context, "Session expired.")
        return ConversationHandler.END
    try:
        days = int(update.message.text.strip())
        if days < 1 or days > 365:
            raise ValueError()
    except Exception:
        await safe_reply(update, context, "Invalid days (1-365).")
        return S_ENTER_DAYS
    create['data']['days'] = days
    context.user_data['create'] = create
    await safe_reply(update, context, "Enter short description for the deal (one message):")
    return S_ENTER_DESC

async def create_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create = context.user_data.get('create')
    if not create:
        await safe_reply(update, context, "Session expired.")
        return ConversationHandler.END
    desc = update.message.text.strip()[:900]
    create['data']['description'] = desc
    d = create['data']
    # check presence
    missing = [k for k in ('buyer_id','seller_id','escrower_id','amount','currency','days') if k not in d]
    if missing:
        await safe_reply(update, context, f"Missing fields: {missing}. Cancel and retry.", reply_markup=MAIN_MENU)
        context.user_data.pop('create', None)
        return ConversationHandler.END
    buyer = get_user(d['buyer_id']); seller = get_user(d['seller_id']); escrower = get_user(d['escrower_id'])
    bio_verified = bool(buyer and buyer['bio_verified'])
    fee = fee_for_amount(d['amount'], bio_verified)
    escrow_to = escrow_till_iso(d['days'])
    summary = f"""📝 Deal Summary

Buyer: @{buyer['username']} ({buyer['id']})
Seller: @{seller['username']} ({seller['id']})
Escrower: @{escrower['username']} ({escrower['id']})
Amount: {d['amount']} {d['currency']}
Fee: {fee}
Time to complete: {d['days']} days
Escrow till: {escrow_to}
Description: {d['description']}

Confirm to create deal.
"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm", callback_data="create:confirm"), InlineKeyboardButton("❌ Cancel", callback_data="create:cancel")]])
    await safe_reply(update, context, summary, reply_markup=kb)
    return S_CONFIRM

async def cb_create_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "create:cancel":
        await safe_reply(q, context, "Deal creation cancelled.", reply_markup=MAIN_MENU)
        context.user_data.pop('create', None)
        return ConversationHandler.END
    create = context.user_data.get('create')
    if not create:
        await safe_reply(q, context, "Session expired.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    d = create['data']
    # re-check verified
    if not (require_verified(d['buyer_id'], 'buyer') and require_verified(d['seller_id'], 'seller') and require_verified(d['escrower_id'], 'escrower')):
        await safe_reply(q, context, "All participants must be verified buyer/seller/escrower. Request verification and try again.", reply_markup=MAIN_MENU)
        context.user_data.pop('create', None)
        return ConversationHandler.END
    buyer = get_user(d['buyer_id'])
    bio_verified = bool(buyer and buyer['bio_verified'])
    fee = fee_for_amount(d['amount'], bio_verified)
    txid = generate_unique_txid(d['buyer_id'], d['seller_id'], d['escrower_id'])
    escrow_till = escrow_till_iso(d['days'])
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO deals(txid, buyer_id, seller_id, admin_id, amount, currency, fee, status,
                   time_to_complete_days, escrow_till, description, chat_id, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (txid, d['buyer_id'], d['seller_id'], d['escrower_id'], d['amount'], d['currency'], fee,
                 "PENDING_PAYMENT", d['days'], escrow_till, d['description'], create.get('chat_id'), now_iso(), now_iso()))
    conn.commit()
    conn.close()
    add_log(txid, q.from_user.id, "CREATE")
    # notify parties
    try:
        await context.bot.send_message(d['buyer_id'], f"Deal created: TXID {txid}. Please upload payment screenshot with caption: /paid {txid}")
    except Exception:
        pass
    try:
        await context.bot.send_message(d['seller_id'], f"Deal created: {txid}. Wait for buyer's payment proof.")
    except Exception:
        pass
    try:
        await context.bot.send_message(d['escrower_id'], f"You are assigned as Escrower for {txid}.")
    except Exception:
        pass
    # notify group if present
    if create.get('chat_id'):
        try:
            await context.bot.send_message(create['chat_id'], f"New deal {txid} created. Amount {d['amount']}{d['currency']}.")
        except Exception:
            pass
    await safe_reply(q, context, f"✅ Deal created. TXID: {txid}\nFee: {fee} {d['currency']}", reply_markup=MAIN_MENU)
    context.user_data.pop('create', None)
    return ConversationHandler.END

async def cb_create_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await safe_reply(q, context, "Deal creation cancelled.", reply_markup=MAIN_MENU)
    context.user_data.pop('create', None)
    return ConversationHandler.END

# ---------------- Payment upload handler ----------------
async def handle_paid_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.photo:
        return
    caption = (msg.caption or "").strip()
    if not caption:
        await safe_reply(update, context, "Please send a photo with caption: /paid <TXID>", reply_markup=MAIN_MENU)
        return
    parts = caption.split()
    if len(parts) < 2 or parts[0].lower() != "/paid":
        await safe_reply(update, context, "Caption format: /paid <TXID>", reply_markup=MAIN_MENU)
        return
    txid = parts[1].strip().upper()
    user = update.effective_user
    register_user_if_missing(user)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM deals WHERE txid=?", (txid,))
    deal = cur.fetchone()
    if not deal:
        conn.close()
        await safe_reply(update, context, "TXID not found.", reply_markup=MAIN_MENU)
        return
    if user.id != deal['buyer_id']:
        conn.close()
        await safe_reply(update, context, "Only the buyer may upload payment proof for this deal.", reply_markup=MAIN_MENU)
        return
    if deal['status'] != "PENDING_PAYMENT":
        conn.close()
        await safe_reply(update, context, f"Cannot upload proof in current status: {deal['status']}", reply_markup=MAIN_MENU)
        return
    file_id = msg.photo[-1].file_id
    cur.execute("INSERT INTO payments(txid, uploaded_by, file_id, file_path, approved, uploaded_at) VALUES (?,?,?,?,?,?)",
                (txid, user.id, file_id, None, 0, now_iso()))
    cur.execute("UPDATE deals SET status=?, updated_at=? WHERE txid=?", ("AWAITING_DELIVERY", now_iso(), txid))
    conn.commit()
    conn.close()
    add_log(txid, user.id, "UPLOAD_PROOF")
    await safe_reply(update, context, f"Payment proof uploaded for {txid}. Admins will review.", reply_markup=MAIN_MENU)
    # notify seller/admin
    try:
        await context.bot.send_message(deal['seller_id'], f"Buyer uploaded proof for {txid}. Please deliver.")
    except Exception:
        pass
    if deal['admin_id']:
        try:
            await context.bot.send_message(deal['admin_id'], f"Payment proof for {txid} awaiting review.")
        except Exception:
            pass

# ---------------- Payment approval (admin) ----------------
async def cmd_approve_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in INITIAL_ADMIN_IDS and not require_verified(user.id, 'escrower'):
        await safe_reply(update, context, "Not authorized.", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, txid, uploaded_by, file_id FROM payments WHERE approved=0 ORDER BY uploaded_at ASC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await safe_reply(update, context, "No pending payments.", reply_markup=MAIN_MENU)
        return
    for p in rows:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"payment:approve:{p['id']}"),
                                    InlineKeyboardButton("❌ Reject", callback_data=f"payment:reject:{p['id']}")]])
        try:
            if p['file_id']:
                await context.bot.send_photo(update.effective_chat.id, p['file_id'], caption=f"Payment id:{p['id']} TXID:{p['txid']}", reply_markup=kb)
            else:
                await safe_reply(update, context, f"Payment id:{p['id']} TXID:{p['txid']}", reply_markup=kb)
        except Exception:
            await safe_reply(update, context, f"Payment id:{p['id']} TXID:{p['txid']}", reply_markup=kb)

async def cb_payment_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 3:
        await safe_reply(q, context, "Invalid.", reply_markup=MAIN_MENU)
        return
    _, action, pid_s = parts
    pid = int(pid_s)
    actor = q.from_user
    if actor.id not in INITIAL_ADMIN_IDS and not require_verified(actor.id, 'escrower'):
        await safe_reply(q, context, "Not authorized.", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT txid, uploaded_by FROM payments WHERE id=?", (pid,))
    p = cur.fetchone()
    if not p:
        conn.close()
        await safe_reply(q, context, "Payment not found.", reply_markup=MAIN_MENU)
        return
    tx = p['txid']
    if action == "approve":
        cur.execute("UPDATE payments SET approved=1 WHERE id=?", (pid,))
        cur.execute("UPDATE deals SET status=?, updated_at=? WHERE txid=?", ("AWAITING_CONFIRMATION", now_iso(), tx))
        conn.commit()
        conn.close()
        add_log(tx, actor.id, "PAYMENT_APPROVED")
        await safe_reply(q, context, f"Payment {pid} approved for {tx}.", reply_markup=MAIN_MENU)
        try:
            await context.bot.send_message(p['uploaded_by'], f"Your payment for {tx} was approved.")
        except Exception:
            pass
        deal = get_deal(tx)
        if deal:
            try:
                await context.bot.send_message(deal['seller_id'], f"Payment for {tx} approved; you may deliver.")
            except Exception:
                pass
    else:
        cur.execute("DELETE FROM payments WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        add_log(tx, actor.id, "PAYMENT_REJECTED")
        await safe_reply(q, context, f"Payment {pid} rejected and removed.", reply_markup=MAIN_MENU)
        try:
            await context.bot.send_message(p['uploaded_by'], f"Your payment for {tx} was rejected by admin.")
        except Exception:
            pass

# ---------------- Delivered / confirm / cancel ----------------
def get_deal(txid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM deals WHERE txid=?", (txid,))
    r = cur.fetchone()
    conn.close()
    return r

async def cmd_delivered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await safe_reply(update, context, "Usage: /delivered <TXID>", reply_markup=MAIN_MENU)
        return
    txid = context.args[0].strip().upper()
    actor = update.effective_user
    deal = get_deal(txid)
    if not deal:
        await safe_reply(update, context, "TXID not found.", reply_markup=MAIN_MENU)
        return
    if actor.id != deal['seller_id']:
        await safe_reply(update, context, "Only the seller may mark delivered.", reply_markup=MAIN_MENU)
        return
    if deal['status'] != "AWAITING_DELIVERY":
        await safe_reply(update, context, f"Cannot mark delivered (status={deal['status']}).", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE deals SET status=?, updated_at=? WHERE txid=?", ("AWAITING_CONFIRMATION", now_iso(), txid))
    conn.commit()
    conn.close()
    add_log(txid, actor.id, "DELIVERED")
    await safe_reply(update, context, f"Marked {txid} delivered. Buyer may /confirm {txid}.", reply_markup=MAIN_MENU)

async def cmd_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await safe_reply(update, context, "Usage: /confirm <TXID>", reply_markup=MAIN_MENU)
        return
    txid = context.args[0].strip().upper()
    actor = update.effective_user
    deal = get_deal(txid)
    if not deal:
        await safe_reply(update, context, "TXID not found.", reply_markup=MAIN_MENU)
        return
    if actor.id != deal['buyer_id']:
        await safe_reply(update, context, "Only the buyer may confirm.", reply_markup=MAIN_MENU)
        return
    if deal['status'] != "AWAITING_CONFIRMATION":
        await safe_reply(update, context, f"Cannot confirm now. Status: {deal['status']}", reply_markup=MAIN_MENU)
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE deals SET status=?, updated_at=? WHERE txid=?", ("COMPLETED", now_iso(), txid))
    conn.commit()
    conn.close()
    add_log(txid, actor.id, "CONFIRMED")
    await safe_reply(update, context, f"✅ Deal {txid} confirmed and completed.", reply_markup=MAIN_MENU)

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await safe_reply(update, context, "Usage: /cancel <TXID>", reply_markup=MAIN_MENU)
        return
    txid = context.args[0].strip().upper()
    actor = update.effective_user
    deal = get_deal(txid)
    if not deal:
        await safe_reply(update, context, "TXID not found.", reply_markup=MAIN_MENU)
        return
    if actor.id not in (deal['buyer_id'], deal['seller_id']) and actor.id not in INITIAL_ADMIN_IDS and not require_verified(actor.id, 'escrower'):
        await safe_reply(update, context, "Only buyer/seller or trusted admin may cancel.", reply_markup=MAIN_MENU)
        return
    if deal['status'] in ("COMPLETED", "REFUNDED"):
        await safe_reply(update, context, "Cannot cancel completed/refunded deal.", reply_markup=MAIN_MENU)
        return
    cancel_fee = round(deal['amount'] * (CANCEL_FEE_PERCENT / 100.0), 2)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE deals SET status=?, updated_at=? WHERE txid=?", ("CANCELLED", now_iso(), txid))
    conn.commit()
    conn.close()
    add_log(txid, actor.id, "CANCELLED", f"fee={cancel_fee}")
    await safe_reply(update, context, f"Deal {txid} cancelled. Cancel fee: {cancel_fee}.", reply_markup=MAIN_MENU)

# ---------------- mydeals and pdf ----------------
async def cmd_mydeals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT txid, amount, currency, status, created_at FROM deals WHERE buyer_id=? OR seller_id=? OR admin_id=? ORDER BY created_at DESC LIMIT 30", (user.id, user.id, user.id))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await safe_reply(update, context, "No deals found for you.", reply_markup=MAIN_MENU)
        return
    lines = [f"{r['txid']} | {r['amount']}{r['currency']} | {r['status']} | {r['created_at']}" for r in rows]
    await safe_reply(update, context, "\n".join(lines), reply_markup=MAIN_MENU)

async def cmd_getpdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT txid FROM deals ORDER BY created_at DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await safe_reply(update, context, "No deals to show.", reply_markup=MAIN_MENU)
        return
    kb = [[InlineKeyboardButton(r['txid'], callback_data=f"pdf:{r['txid']}")] for r in rows]
    kb.append([InlineKeyboardButton("Main Menu", callback_data="menu:main")])
    await safe_reply(update, context, "Select deal for PDF:", reply_markup=InlineKeyboardMarkup(kb))

async def cb_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not q.data.startswith("pdf:"):
        await safe_reply(q, context, "Invalid.", reply_markup=MAIN_MENU)
        return
    txid = q.data.split(":",1)[1]
    deal = get_deal(txid)
    if not deal:
        await safe_reply(q, context, "Deal not found.", reply_markup=MAIN_MENU)
        return
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold", 14); c.drawString(40,y,"Escrow Deal Report"); y -= 30
    c.setFont("Helvetica", 11)
    fields = [
        ("TXID", deal['txid']), ("Buyer", deal['buyer_id']), ("Seller", deal['seller_id']), ("Escrower", deal['admin_id']),
        ("Amount", f"{deal['amount']} {deal['currency']}"), ("Fee", str(deal['fee'])), ("Status", deal['status']),
        ("Time to complete", str(deal['time_to_complete_days'])), ("Escrow Till", deal['escrow_till']),
        ("Description", str(deal['description'])), ("Created At", deal['created_at']), ("Updated At", deal['updated_at'])
    ]
    for k,v in fields:
        c.drawString(40, y, f"{k}: {v}")
        y -= 18
        if y < 40:
            c.showPage(); y = 800
    c.showPage(); c.save(); buf.seek(0)
    await context.bot.send_document(chat_id=q.message.chat_id, document=InputFile(buf, filename=f"escrow_{txid}.pdf"))
    await safe_reply(q, context, f"PDF sent for {txid}.", reply_markup=MAIN_MENU)

# ---------------- admin list ----------------
async def cmd_adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role='escrower' AND verified=1")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        await safe_reply(update, context, "No trusted escrowers found.", reply_markup=MAIN_MENU)
        return
    lines = [f"@{r['username']} (id:{r['id']})" for r in rows]
    await safe_reply(update, context, "Trusted Escrowers:\n" + "\n".join(lines), reply_markup=MAIN_MENU)

# ---------------- Main menu callback dispatcher ----------------
async def cb_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    payload = q.data.split(":",1)[1] if ":" in q.data else q.data
    if payload == "create":
        return await create_entry(update, context)
    if payload == "mydeals":
        return await cmd_mydeals(update, context)
    if payload == "getpdf":
        return await cmd_getpdf(update, context)
    if payload == "upload":
        return await safe_reply(q, context, "To upload payment proof: send a photo with caption `/paid <TXID>`", reply_markup=MAIN_MENU, parse_mode="HTML")
    if payload == "reqverify":
        user = q.from_user
        return await safe_reply(q, context, "Click to request verification:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Request Verification", callback_data=f"reqverify:{user.id}")],[InlineKeyboardButton("Main Menu", callback_data="menu:main")]]))
    if payload == "become_escrower":
        await cmd_become_escrower_inline(q.from_user, context)
        return await safe_reply(q, context, "Escrower request sent to admins.", reply_markup=MAIN_MENU)
    if payload == "setrole":
        return await safe_reply(q, context, "Select your role:", reply_markup=ROLE_KB)
    if payload == "help":
        return await safe_reply(q, context, "Help & Guide", reply_markup=HELP_KB)

async def cmd_become_escrower_inline(user, context):
    register_user_if_missing(user)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO pending_escrowers(id, username, requested_at) VALUES (?,?,?)",
                (user.id, user.username or f"user{user.id}", now_iso()))
    conn.commit()
    conn.close()
    for aid in INITIAL_ADMIN_IDS:
        try:
            await context.bot.send_message(aid, f"User @{user.username or user.id} requested escrower role. Use /pending_escrowers to review.")
        except Exception:
            pass

# ---------------- General help topic callbacks ----------------
async def cb_help_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    topic = q.data.split(":",1)[1]
    if topic == "create":
        text = "Create a deal via the inline 'Create Deal' menu. Flow: select buyer → seller → escrower → amount → currency → days → description → confirm."
    elif topic == "upload":
        text = "Upload payment: send a photo with caption `/paid <TXID>`. Only buyer may upload."
    elif topic == "fees":
        text = f"Fees: {ESCROW_FEE_PERCENT}% escrow fee. Cancel fee: {CANCEL_FEE_PERCENT}%. Extra if buyer not bio-verified: {EXTRA_NO_BIO_FEE_PERCENT}%."
    elif topic == "admins":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE role='escrower' AND verified=1")
        rows = cur.fetchall(); conn.close()
        if not rows:
            text = "No verified escrowers."
        else:
            text = "Escrowers:\n" + "\n".join([f"@{r['username']} (id:{r['id']})" for r in rows])
    else:
        text = "Topic not found."
    await safe_reply(q, context, text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Main Menu", callback_data="menu:main")]]))

# ---------------- Error handler ----------------
async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled error: %s", context.error)
    for aid in INITIAL_ADMIN_IDS:
        try:
            await context.bot.send_message(aid, f"Bot error: {context.error}")
        except Exception:
            pass

# ---------------- App wiring ----------------
def build_app():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # core commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("pending_escrowers", cmd_pending_escrowers))
    app.add_handler(CommandHandler("approve_payments", cmd_approve_payments))
    app.add_handler(CommandHandler("delivered", cmd_delivered))
    app.add_handler(CommandHandler("confirm", cmd_confirm))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("mydeals", cmd_mydeals))
    app.add_handler(CommandHandler("getpdf", cmd_getpdf))
    app.add_handler(CommandHandler("adminlist", cmd_adminlist))

    # conversation for create flow
    conv = ConversationHandler(
        entry_points=[CommandHandler("create", create_entry),
                      CallbackQueryHandler(create_entry, pattern="^menu:create$")],
        states={
            S_SELECT_BUYER: [
                CallbackQueryHandler(cb_pick, pattern=r"^pick:buyer:\d+$"),
                CallbackQueryHandler(cb_nav, pattern=r"^nav:buyer:\d+$"),
                CallbackQueryHandler(cb_create_cancel, pattern=r"^create:cancel$")
            ],
            S_SELECT_SELLER: [
                CallbackQueryHandler(cb_pick, pattern=r"^pick:seller:\d+$"),
                CallbackQueryHandler(cb_nav, pattern=r"^nav:seller:\d+$"),
                CallbackQueryHandler(cb_create_cancel, pattern=r"^create:cancel$")
            ],
            S_SELECT_ESCROWER: [
                CallbackQueryHandler(cb_pick, pattern=r"^pick:escrower:\d+$"),
                CallbackQueryHandler(cb_nav, pattern=r"^nav:escrower:\d+$"),
                CallbackQueryHandler(cb_create_cancel, pattern=r"^create:cancel$")
            ],
            S_ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_amount)],
            S_ENTER_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_currency)],
            S_ENTER_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_days)],
            S_ENTER_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_desc)],
            S_CONFIRM: [
                CallbackQueryHandler(cb_create_confirm, pattern=r"^create:confirm$"),
                CallbackQueryHandler(cb_create_cancel, pattern=r"^create:cancel$")
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: (c.user_data.pop('create', None), u.message.reply_text("Cancelled.", reply_markup=MAIN_MENU)))],
        allow_reentry=True
    )
    app.add_handler(conv)

    # inline callbacks
    app.add_handler(CallbackQueryHandler(cb_role_select, pattern=r"^role:"))
    app.add_handler(CallbackQueryHandler(cb_reqverify, pattern=r"^reqverify:"))
    app.add_handler(CallbackQueryHandler(cb_verify_user, pattern=r"^verify_user:"))
    app.add_handler(CallbackQueryHandler(cb_main_menu, pattern=r"^menu:"))
    app.add_handler(CallbackQueryHandler(cb_help_topic, pattern=r"^help:"))
    app.add_handler(CallbackQueryHandler(cb_nav, pattern=r"^nav:"))
    app.add_handler(CallbackQueryHandler(cb_pick, pattern=r"^pick:"))
    app.add_handler(CallbackQueryHandler(cb_create_confirm, pattern=r"^create:confirm$"))
    app.add_handler(CallbackQueryHandler(cb_create_cancel, pattern=r"^create:cancel$"))
    app.add_handler(CallbackQueryHandler(cb_payment_action, pattern=r"^payment:"))
    app.add_handler(CallbackQueryHandler(cb_pdf, pattern=r"^pdf:"))
    app.add_handler(CallbackQueryHandler(cb_esc_approve, pattern=r"^esc_approve:"))

    # help topic callback
    app.add_handler(CallbackQueryHandler(cb_help_topic, pattern=r"^help:"))

    # message handlers
    app.add_handler(MessageHandler(filters.PHOTO & (~filters.COMMAND), handle_paid_photo))

    app.add_error_handler(on_error)
    return app

def main():
    init_db()
    app = build_app()
    logger.info("Starting escrow_bot_fixed...")
    app.run_polling()

if __name__ == "__main__":
    main()

