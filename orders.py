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
    if order != None and 'data' in order:
        return order['data']['status']
    else:
        if order != None and 'msg' in order:
            return order['msg'] 
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
        return data

def get_open_orders(net=config['mainnet']):
    url = f"{net}/api/v2/balance"
    try:
        data = get(url,{"address": f"{config['viteconnect_address']}"}).json()
    except:
        data = get(url,{"address": f"{config['delegation_address']}"}).json()
    if data['data']:
        return data['data']
    else:
        return "No Open Orders For Address", data

def get_active_positions(cache):
    active_list = []
    for symbol in cache:
        if cache[symbol]['data']['active'] == True:
            active_list.append(symbol)
    if len(active_list) > 0:
        return active_list
    else:
        active_list.append("No Active Positions")
        return active_list

def get_pnl(cache):
    pnl = {}
    active = get_active_positions(cache)
    if "No Active Positions" not in active:
        for symbol in active:
            size = cache[symbol]['data']['size']
            pnl_calc = (cache[symbol]['data']['entry'] * size) - (cache[symbol]['ohlc']['close'][0] * size)
            pnl[symbol] = pnl_calc
        return pnl
    else:
        pnl = ['No Active Positions']
        return pnl
            
            
def get_tpsl(entry_price, side: int):
    if side:
        entry_price = 0.001064
        sl_prc, tp_prc = 10, 10
        sl_prc = config['stoploss']/100 * entry_price
        tp_prc = config['takeprofit']/100 * entry_price
        stoploss = entry_price + sl_prc
        takeprofit = entry_price - tp_prc
        return stoploss, takeprofit
    else:  
        sl_prc = config['stoploss']/100 * entry_price
        tp_prc = config['takeprofit']/100 * entry_price
        stoploss = entry_price - sl_prc
        takeprofit = entry_price + tp_prc
        return stoploss, takeprofit

def position_size(close):
    size = config['size']
    if config['dynamic_size']:
        data = get_balance()
        quote = config['quote_currency']
        if type(data['data']) == dict:
            quote_bal = float(data[quote]['available'])
            size = round(quote_bal / float(close),3)
            return str(size)
    size=1
    return size
            
        
def create_sig(tx):
    '''
    Create HMAC SHA256 Signature
    '''
    print("l76 - creating signature")
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
    stimestamp= int(str(time()*1000).split(".")[0])
    serverTime= get_time()
    len(serverTime)
    new_time = serverTime - stimestamp
    if (stimestamp < (serverTime + 1000) and (serverTime - stimestamp) <= 5000):
        #TX STRING
        tx = fr"amount={size}&key={key}&price={price}&side={side}&symbol={symbol}&timestamp={stimestamp}"
        signature = create_sig(tx)
        #API CALL
        data = {
            'amount': size,
            'key': config['vite_key'],
            'price': '0.09',
            'side': '0',
            'symbol': symbol,
            'timestamp': str(stimestamp),
            'signature': signature
        }
        print("l104 - sending order!")
        response = requests.post(mainnet+endpoint, data=data)
        r = json.loads(response.text)
        return r
    else:
        print("Server Time Error!")
        # reject request
        
def buy_set(live, order, sl, tp, data, message, entry, size, active=True):
    if order != None and 'data' in order.keys() or not live:
        if live:
            data['orderId'] = order['data']['orderId']
            data['buy_status'] = order_status(order)
        else:
            data['buy_status'] = 'Filled'
        data['flagged'] = True
        data['size'] = size
        data['entry'] = entry
        data['active'] = active
        data['stoploss'] = sl
        data['takeprofit'] = tp
        data['message'] = message
        data['side'] = 'buy'
        data['timestamp'] = time()
    else:
        if live:
            data['message'] = f"{order['code']} -  {order['msg']}"
        data['size'] = None
        data['entry'] = None
        data['flagged'] = False
        data['active'] = False
        data['buy_status'] = None
        data['stoploss'] = None
        data['takeprofit'] = None
        data['side'] = None
    return data
        

def sell_set(live, order, data, message, entry, active=False):
    if (order != None and 'data' in order) or not live:
        if live:
            data['orderId'] = order['data']['orderId']
            data['sell_status'] = order_status(order)
        else:
            data['sell_status'] = 'Filled'
        data['entry'] = entry
        data['flagged'] = True
        data['active'] = active
        data['message'] = message
        data['side'] = 'sell'
    else:
        if live:
            data['message'] = f"{order['code']} -  {order['msg']}"
        data['entry'] = None
        data['flagged'] = False
        data['active'] = False
        data['sell_status'] = None
        data['orderId'] = None
    return data