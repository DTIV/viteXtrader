import json
import requests
from time import time
import hmac
import hashlib
from functions import get_time, get_all_pairs
from requests import get, post

f = open("config.json")
config = json.load(f)

key = config['vite_key']

def order_status(order):
    if 'data' in order:
        status = order['data']['status']
        status_list=["Unknown","Pending Request", "Received", "Open", "Filled", "Partially Filled", "Pending Cancel", "	Cancelled", "Partially Cancelled", "Failed", "Expired"]
        return status_list[status]
    else:
        return None

def get_balance(net=config['mainnet']):
    url = f"{net}/api/v2/balance"
    try:
        data = get(url,{"address": f"{config['viteconnect_address']}"}).json()
    except:
        data = get(url,{"address": f"{config['delegation_address']}"}).json()
    if data['data']:
        return data['data']
    else:
        return "No Balances For Address"

def get_open_orders( net=config['mainnet']):
    url = f"{net}/api/v2/balance"
    try:
        data = get(url,{"address": f"{config['viteconnect_address']}"}).json()
    except:
        data = get(url,{"address": f"{config['delegation_address']}"}).json()
    if data['data']:
        return data['data']
    else:
        return "No Open Orders For Address"
    
def get_tpsl(entry_price, side: int):
    if side:
        sl_prc = config['stoploss']/100 * entry_price
        tp_prc = config['takeprofit']/100 * entry_price
        stoploss = float(round(entry_price + sl_prc,2))
        takeprofit = float(round(entry_price - tp_prc,2))
        return stoploss, takeprofit
    else:
        sl_prc = config['stoploss']/100 * entry_price
        tp_prc = config['takeprofit']/100 * entry_price
        stoploss = float(round(entry_price - sl_prc,2))
        takeprofit = float(round(entry_price + tp_prc,2))
        return stoploss, takeprofit

def position_size(close):
    size = config['size']
    if config['dynamic_size']:
        data = get_balance()
        quote = config['quote_currency']
        if type(data) == dict:
            quote_bal = float(data[quote]['available'])
            size = round(quote_bal / float(close),3)
            return str(size)
    return size
            
        
def create_sig(tx):
    '''
    Create HMAC SHA256 Signature
    '''
    print("l74 - creating signature")
    hash256= bytes(tx, 'utf8')
    secret = bytes(config['vite_secret'], encoding='utf8')
    return hmac.new(secret,hash256, hashlib.sha256).hexdigest()
   
def limit_order(size, price, side, symbol, live):
    '''
    LIMIT ORDER: SIGNATURE NOT VERIFYING!
    '''
    global key
    #time
    endpoint = "/api/v2/order/test"
    mainnet = config['mainnet']
    stimestamp= int(str(time()).split(".")[0])
    serverTime=time()
    size = position_size(price)
    if (stimestamp < (serverTime + 1000) and (serverTime - stimestamp) <= 5000):
        #TX STRING
        tx = fr"amount={size}&key={key}&price={price}&side={side}&symbol={symbol}&timestamp={get_time()}"
        signature = create_sig(tx)
        #API CALL
        data = {
            'amount': size,
            'key': config['vite_key'],
            'price': '0.09',
            'side': '0',
            'symbol': symbol,
            'timestamp': str(get_time()),
            'signature': signature
        }
        print("l104 - sending order!")
        response = requests.post(mainnet+endpoint, data=data)
        r = json.loads(response.text)
        return r
    else:
        print("Server Time Error!")
        # reject request
        
def buy_set(live, order, sl, tp, data, message, active=True):
    if 'data' in order or not live:
        data['flagged'] = True
        data['active'] = active
        data['buy_status'] = order_status(order)
        data['stoploss'] = sl
        data['takeprofit'] = tp
        data['message'] = message
        data['orderId'] = order['data']['orderId']
        data['side'] = 'buy'
        return data
    else:
        data['flagged'] = False
        data['active'] = False
        data['message'] = message
        data['buy_status'] = None
        data['stoploss'] = None
        data['takeprofit'] = None
        data['orderId'] = None
        return data
        

def sell_set(live, order, data, message, active=False):
    if 'data' in order or not live:
        data['flagged'] = True
        data['active'] = active
        data['message'] = message
        data['sell_status'] = order_status(order)
        data['orderId'] = order['data']['orderId']
        data['side'] = 'sell'
        return data
    else:
        data['flagged'] = False
        data['message'] = message
        data['active'] = False
        data['sell_status'] = None
        data['orderId'] = None
        return data