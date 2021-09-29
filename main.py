from strategy import strategy
import json
import orders as ordr
import functions as fn
from time import time, sleep

f = open("config.json")
config = json.load(f)
#TODO: get locked amounts for limit order to sell position or try close order call
#whitelist = config['whitelist']
interval = config['interval']
live = config['live']
whitelist=config['whitelist']

def main(cache):
    global whitelist, counter
    print("l16 - starting main loop")
    '''
    WHITELIST LOOP
    '''
    try:
       
        order = None
        for symbol in whitelist:
            cache[symbol]['data']['message'] = None
            dataframe = strategy(symbol, interval)
            cache[symbol]['ohlc'] = dataframe
            data = cache[symbol]['data']
            data['symbol'] = symbol
            if data['active'] == False:
                print("UN-ACTIVE PAIR: ", symbol," ", data['active'])
               
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
                            size = ordr.position_size(dataframe['close'][0])
                            order = ordr.limit_order(size=size, price=dataframe['close'][0], side=0, symbol=symbol, live=True)
                            #STOPLOSS TAKEPROFIT
                            stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], side=0)
                            #DATA
                            ordr.buy_set(live, order, round(stoploss,6), round(takeprofit,6), data, message, entry=dataframe['close']['0'], size=size)
                        else:
                            size = ordr.position_size(dataframe['close'][0])
                            order = None
                            stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], side=0)
                            ordr.buy_set(live=False,order=order, sl=round(stoploss,6), tp=round(takeprofit,6), data=data, message=message,entry=dataframe['close'][0], size=size)
                    '''
                    SHORT ORDER
                    '''
                    if dataframe['sell'][0] == 1:
                        message = f"SHORT SIGNAL FOR {symbol} at {dataframe['close'][0]}"
                        print(message)
                        if live:
                            #LIMIT 
                            size = ordr.position_size(dataframe['close'][0])
                            order = ordr.limit_order(size=size, price=dataframe['close'][0], side=1, symbol=symbol, live=True)
                            #STOPLOSS TAKEPROFIT
                            stoploss, takeprofit = ordr.get_tpsl(dataframe['close'][0], 1)
                            #DATA
                            ordr.sell_set(True, order, data, message=message, entry=dataframe['close']['0'])
                        else:
                            ordr.sell_set(False, order, data, message=message, entry=dataframe['close']['0'])
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
                print("ACTIVE PAIR: ", symbol," ", data['active'])
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
                                size = ordr.position_size(dataframe['close'][0])
                                order = ordr.limit_order(size, dataframe['close'][0],1, symbol, live)
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
                                size = ordr.position_size(dataframe['close'][0])
                                order = ordr.limit_order(size, dataframe['close'][0],1, symbol, live)
                                ordr.sell_set(True, order, data, message)
                            else:
                                ordr.sell_set(True, order, data, message)
                                
                        '''
                        STOPLOSS & TAKEPROFIT
                        '''
                        if cache[symbol]['stoploss'] != None:
                            message = f"!!! STOPLOSS !!! LONG POSITION CLOSED FOR {symbol}  at {dataframe['close'][0]}"
                            print(message)
                            if dataframe['close'][0] < cache[symbol]['stoploss']:
                                if live:
                                    
                                    size = ordr.position_size(dataframe['close'][0])
                                    order = ordr.limit_order(size, dataframe['close'][0],1, symbol, live)
                                    ordr.sell_set(True, order, data, message)
                                else:
                                    ordr.sell_set(True, order, data, message)
                        if cache[symbol]['takeprofit'] != None:
                            message = f"!!! TAKEPROFIT !!! LONG POSITION CLOSED FOR {symbol} at {dataframe['close'][0]}"
                            print(message)
                            if dataframe['close'][0] > cache[symbol]['takeprofit']:
                                if live: 
                                    order = ordr.limit_order(size, dataframe['close'][0],1, symbol, live)
                                    ordr.sell_set(True, order, data, message)
                                else:
                                    ordr.sell_set(True, order, data, message)            
                except Exception as e:
                    print("ERROR:", symbol, e)
                    pass
        print("l133 - returning data back to vitetrader")
    except Exception as e:
        print(e)
        pass
    return cache
        