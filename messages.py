import json

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

/whitelist : List of current trading pairs
/timeframes : List of time intervals

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

def timeframe_msg():
    timeframes = list({'5m': '5m', '15m': '15m', '30m': '30m', '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h', '1d': '1d', '3d': '3d', '1w': '1w'})
    return " ".join(timeframes)

def get_whitelist():
    return '\n'.join(config['whitelist'])

