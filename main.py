from strategy import strategy
import json
import orders as ordr
import functions as fn
from time import time, sleep

f = open("config.json")
config = json.load(f)

#whitelist = config['whitelist']
interval = config['interval']
live = config['live']

cache = {}
def main(cache):
    print("l16 - starting main loop")
    '''
    WHITELIST LOOP
    '''
    try:
        whitelist=config['whitelist']
        order = None
        for symbol in whitelist:
            data = fn.get_cache(symbol)
            dataframe = strategy(symbol, interval)
            cache[symbol] = {
                'ohlc': dataframe,
                'data': data[symbol]
                }
            data = cache[symbol]['data']
            data['symbol'] = symbol
            data['timestamp'] = time()
            if data['active'] == False:
               
                '''
                UNOPEN PAIRS LOOP
                '''
                try:
                    '''
                    BUY ORDER
                    '''
                    if dataframe['buy'][0] == 1:
                        message = f"BUY ORDER PLACED FOR {symbol} at {dataframe['close'][0]}"
                        print(message)
                        if live:
                            #LIMIT ORDER
                            order = ordr.limit_order(size=1, price=dataframe['close'][0], side=0, symbol=symbol, live=True)
                            #STOPLOSS TAKEPROFIT
                            stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], 0)
                            #DATA
                            ordr.buy_set(True, order, stoploss, takeprofit, data, message=message)
                        else:
                            stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], 0)
                            ordr.buy_set(False, order, stoploss, stoploss, data, message=message)                     
                    '''
                    SHORT ORDER
                    '''
                    if dataframe['sell'][0] == 1:
                        message = f"SHORT SIGNAL FOR {symbol} at {dataframe['close'][0]}"
                        print(message)
                        if live:
                            #LIMIT ORDER
                            order = ordr.limit_order(dataframe['close'][0], 1, symbol, True)
                            #STOPLOSS TAKEPROFIT
                            stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], 1,True)
                            #DATA
                            ordr.sell_set(True, order, data, message=message)
                        else:
                            ordr.sell_set(False, order, data, message=message)
                        if data['sell_status'] == 'Filled':
                            if data['active'] == True:
                                #SET STOPLOSS AND TAKEPROFIT
                                stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], 1,True)
                                data['stoploss'] = stoploss
                                data['takeprofit'] = takeprofit
                except Exception as e:
                    print("ERROR:", symbol, e)
                    pass
            else:
                '''
                OPEN PAIRS LOOP
                '''
                try:
                    if data['side'] == 0:
                        '''
                        SELL ORDER
                        '''
                        if dataframe['sell'][0] == 1:
                            message = f"LONG POSITION CLOSED FOR {symbol} - {interval} at {dataframe['close'][0]}"
                            print(message)
                            #CLOSING OPEN PAIR
                            if live:
                                order = ordr.limit_order(dataframe['close'][0], 1, symbol, True)
                                ordr.sell_set(True, order, data, message=message)
                            else:
                                ordr.sell_set(False, order, data)
                        '''
                        BUY CLOSE
                        '''
                        if dataframe['buy_close'][0] == 1:
                            message = f"LONG POSITION CLOSED FOR {symbol} - at {dataframe['close'][0]}"
                            print(message)
                            if live:
                                order = ordr.limit_order(dataframe['close'][0], 1, symbol, True)
                                ordr.sell_set(True, order, data, message)
                            else:
                                ordr.sell_set(True, order, data, message)
                                
                        '''
                        STOPLOSS & TAKEPROFIT
                        '''
                        if cache[symbol]['stoploss']:
                            message = f"!!! STOPLOSS !!! LONG POSITION CLOSED FOR {symbol}  at {dataframe['close'][0]}"
                            print(message)
                            if dataframe['close'][0] < cache[symbol]['stoploss']:
                                if live: 
                                    order = ordr.limit_order(dataframe['close'][0], 1, symbol, True)
                                    ordr.sell_set(True, order, data, message)
                                else:
                                    ordr.sell_set(True, order, data, message)
                        if cache[symbol]['takeprofit']:
                            message = f"!!! TAKEPROFIT !!! LONG POSITION CLOSED FOR {symbol} at {dataframe['close'][0]}"
                            print(message)
                            if dataframe['close'][0] > cache[symbol]['takeprofit']:
                                if live: 
                                    order = ordr.limit_order(dataframe['close'][0], 1, symbol, True)
                                    ordr.sell_set(True, order, data, message)
                                else:
                                    ordr.sell_set(True, order, data, message)            
                except Exception as e:
                    print("ERROR:", symbol, e)
                    pass
        return cache
    except Exception as e:
        print(e)
        pass
        