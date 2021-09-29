import json
from functions import get_trading_pair, token_detail


f = open("config.json")
config = json.load(f)


def menu_msg():
    return f"""
COMMANDS

--------------------
/menu : List of commands
--------------------

/start - Start the Vite X Trader
/stop - Stop the bot
--------------------
/balance - get account balances
/open - get open orders
/active - get active positions
/pnl - get Profit and Loss for active positions

/whitelist : List of current trading pairs
/timeframes : List of time intervals

---------------------
$ detail <TRADING_PAIR>  :  detail for a specific trading pair on ViteX
$ detail <SYMBOL>  :  detail for a specific currency on ViteX
"""

def startup_msg():
    return f"""
---------------
Vite X Trader
---------------

/menu - view commands
/start - start bot

Live Mode: {config['live']}
Interval: {config['interval']}
Quote Currency: {config['quote_currency']}

Ready...
"""

def pair_info_msg(symbol, net=config['mainnet']):
    info = get_trading_pair(net, symbol)
    return f"""
{symbol} DETAILS
----------------
{info['tradingCurrencyName']} - {info['quoteCurrencyName']}

Trading Currency ID : {info['tradingCurrencyId']}
Quote Currency ID : {info['quoteCurrencyId']}
Ask : {info['askPrice']}
Bid : {info['bidPrice']}
Last : {info['lastPrice']}
High : {info['highPrice']}
Low : {info['lowPrice']}
Min Order Size: {info['minOrderSize']}
open Buy Orders: {info['openBuyOrders']}
open Sell Orders: {info['openSellOrders']}
"""

def get_token_detail(symbol):
    info = token_detail(symbol)
    data= info['data']
    links = []
    for i in info['data']['links']:
        new_str = f"{i} :  {data['links'][i][0]}"
        links.append(new_str)
    links = "\n".join(links)
    return f"""
{symbol} DETAIL
----------------
{data['name']} - {data['originalSymbol']}

TokenID: {data['tokenId']}
Total Supply: {data['totalSupply']}

OVERVIEW
----------------
{data['overview']['en']}

LINKS
-----------------
{links}
"""


def timeframe_msg():
    timeframes = list({'5m': '5m', '15m': '15m', '30m': '30m', '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h', '1d': '1d', '3d': '3d', '1w': '1w'})
    return " ".join(timeframes)

def get_whitelist():
    return '\n'.join(config['whitelist'])

