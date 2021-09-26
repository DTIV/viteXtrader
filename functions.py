from requests import get
import pandas as pd
import json
import ccxt
import time

f = open("config.json")
config = json.load(f)

binance = ccxt.binance()

def get_time(net=config['mainnet']):
    url = f"{net}/api/v2/timestamp"
    timestamp = get(url).json()
    return timestamp['data']

def set_interval(interval: str):
    set_int = None
    if interval == '1m':
        set_int = 'minute'
    elif interval == '30m':
        set_int = 'minute30'
    elif interval == '1h':
        set_int = 'hour'
    elif interval == '6h':
        set_int = 'hour6'
    elif interval == '12h':
        set_int == 'hour12'
    elif interval == '1d':
        set_int = 'day'
    elif interval == '1w':
        set_int = 'week'
    else:
        set_int = 'hour'
    return set_int
    
def sort_interval(interval: str, interval_list = list(binance.timeframes)):
    minutes = None
    for i in interval_list:
        if i == interval:
            if 'm' in i:
                minutes = int(i.replace('m',""))
            elif 'h' in i:
                minutes = int(i.replace('h',"")) * 60
            elif 'd' in i:
                minutes = int(i.replace('d',"")) * 1440
            else:
                minutes = 60
    return minutes

def get_all_tokens(net: str, dict):
    symbol_list = []
    url = f"{net}/api/v2/tokens"
    data = get(url).json()
    for i in data['data']:
        symbol_list.append(i['symbol'])
        name = i['name']
        dict[name] = {
            "originalSymbol" : i['originalSymbol'],
            "symbol": i['symbol'],
            "tokenId": i['tokenId'],
            "urlIcon": i['urlIcon']
            }
    return dict, symbol_list

def get_trading_pair(net: str, base: str, quote: str):
    url = f"{net}/api/v2/market/"
    data = get(url,{"symbol": f'{base}_{quote}'}).json()
    return data['data']

def get_quote_pairs(quote, pairs_list):
    quote_pairs = []
    for i in pairs_list:
        if f"/{quote}" in i:
            quote_pairs.append(i)
    return quote_pairs

net = config['mainnet']
def get_all_pairs(net):
    pairslist=[]
    binancelist=[]
    symbol_dict = {}
    url = f"{net}/api/v2/markets"
    pairs = get(url).json()
    for i in pairs['data']:
        pairslist.append(i['symbol'])
        new_str = i['symbol'].replace("-000","").replace("-001","").replace("_","/")
        binancelist.append(new_str)
        symbol_dict[new_str] = i['symbol']
    return pairslist, binancelist, symbol_dict

symbol= "BEAM-000_BTC-000"



def market_check(symbol_list):
    binance_list = []
    binance = ccxt.binance()
    b_mrkt = binance.load_markets()
    for i in symbol_list:
        if i in b_mrkt.keys():
            binance_list.append(i)
            symbol_list.pop()
    return binance_list

def cut_symbol(vite_symbol):
    return vite_symbol.replace("-000","").replace("-001","").replace("_","/")

def get_ohlc(symbol, interval, net=config['mainnet']):
    '''
    symbol: vite-type symbol string
    interval: binance-type string
    description: gets ohlc data, if pair in binance, else data from viteX api,
    creates binance symbol, returns dataframe
    '''
    symbol = cut_symbol(symbol)
    pairs, blist, symbol_dict = get_all_pairs(net)
    binance_list = market_check(blist)
    if symbol in binance_list:
        try:
            ohlc = binance.fetchOHLCV(symbol,'5m')
        except:
            time.sleep(0.5)
            ohlc = binance.fetchOHLCV(symbol,'5m')
        df = pd.DataFrame(ohlc)
        df.columns = ["time", 'open','high', 'low', 'close', 'volume']
        df = df.sort_values(by='time',ascending=False,ignore_index=True)
        df['time'] = pd.to_datetime(df['time'], unit='ms')
    else:
        vite_symbol = symbol_dict[symbol]
        interval = set_interval(interval)
        url = f"{net}/api/v2/klines"
        data = get(url,{"symbol": f'{vite_symbol}', "interval": interval, "limit": 500}).json()
        dataframe = pd.DataFrame(data['data'])
        dataframe.columns = ['time','close','open','high','low','volume']
        df = dataframe.sort_values(by='time',ascending=False,ignore_index=True)
        df['time'] = pd.to_datetime(df['time']*1000, unit='ms')
    return df

def get_cache(symbol):
    cache={}
    cache[symbol] = {
        'active': False,
        'flagged': False,
        'buy_status': None,
        'sell_status': None,
        'buy_close': None,
        'sell_close': None,
        'stoploss': None,
        'takeprofit': None,
        'orderId': None,
        'side': None,
        'ohlc': None,
        'message': None,
        }
    return cache
    
def historical_data(cache, whitelist, interval):
    for i in whitelist:
        cache[i] = get_ohlc(i, interval)
    return cache