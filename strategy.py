from ta import add_all_ta_features
from ta import volatility as vlt
from ta import volume as vol
from ta import momentum as mom
from ta import trend as tr
from ta import others as oth
from functions import get_ohlc
import pandas as pd
import copy

def strategy(symbol, interval):
    df=get_ohlc(symbol, interval)[::-1].copy()
    
    '''
    \\\\\\\\\\\\\\\\\\\\   POPULATE INDICATORS   ||||||||||||||||||||
    full indicators list: https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html
    '''
    
    #MACD
    macd = tr.MACD(close=df['close'],window_slow=26,window_fast=12,window_sign=9)
    df['MACD_MAIN'] = macd.macd()
    df['MACD_HIS'] = macd.macd_diff()
    df['MACD_SIG'] = macd.macd_signal()
    
    #BOLLINGER BANDS
    indicator_bb = vlt.BollingerBands(close=df["close"], window=20, window_dev=2)
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()
    
    #RSI
    rsi = mom.RSIIndicator(close=df['close'],window=14)
    df['RSI'] = rsi.rsi()
    
    #SMA
    ma = tr.SMAIndicator(close=df['close'], window=200)
    df['SMA'] = ma.sma_indicator()
    

    '''
    \\\\\\\\\\\\\\\\\\\\   POPULATE CONDITIONS   ||||||||||||||||||||
    '''
    
    def volume_check(df):
        df['volume_check'] = False
        
        if( df['volume'][0] > 0 ):
                #SET FLAGS
                df['volume_check'] = True
        else:
            df['volume_check'] = False
        return df
    
    volume_check(df)
    
    '''
    \\\\\\\\\\\\\\\\\\\\   POPULATE BUY SIGNALS   ||||||||||||||||||||
    '''
    '''
    A Simple Bollinger bands strategy
    '''
    #BUY SIGNAL
    def buy_signal(df):
        "function to generate signal"
        df.loc[
            (
                (df['volume_check'] == True) &
                (df['RSI'][0] < 30) &
                (df['close'][0] < df['bb_bbl'])
            ),
            'buy'] = 1
        return df
    
    df = buy_signal(df)
    #BUY MOVING STOPLOSS
    def buy_close(df):
        df.loc[
            (
                (df['volume_check'] == False)
            ),
            'buy_close'] = 1
        df['buy_close'] = pd.to_numeric(df['buy_close'])
        return df
    buy_close(df)  
    
    '''
    \\\\\\\\\\\\\\\\\\\\   POPULATE SELL SIGNALS   ||||||||||||||||||||
    '''  
    #SELL SIGNAL
    def sell_signal(df):
        df.loc[
            (
                (df['volume_check'] == True) &
                (df['RSI'][0] > 80) &
                (df['close'][0] > df['bb_bbh'])
            ),
            'sell'] = 1
        df['sell'] = pd.to_numeric(df['sell'])
        return df
    sell_signal(df)
    
    #SELL MOVING STOPLOSS
    def sell_close(df):
        df.loc[
            (
                (df['volume_check'] == False)
            ),
            'sell_close'] = 1
        df['sell_close'] = pd.to_numeric(df['sell_close'])
        return df
    sell_close(df)
    return df
