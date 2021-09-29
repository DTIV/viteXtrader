ViteX Trader
------------
This is my submission for Gitcoins Hackathon Round 11 for the "Open Task - Propose And Create Your Own Project - Up To $20,000 In Reward!" for Vite.
Using the ViteX public and private API, this Discord bot is a powerful trading tool and market data explorer. Users can sign transactions and place orders with stoploss and takeprofit, when the user defined strategy parameters are met. Users can access there account balances, current and closed orders, transaction history, profit and loss data, and coin updates either on demand or by status updates.

Volume to ViteX will increase as users stake Vite to get access to private API to place many trades on ViteXTrader or even just getting market data updates provided by ViteX public API's, volume will increase, and it will aslo attract more users looking for a easy-to-use all-purpose bot, or a open-source project to build on, and trade there favourite pairs trading on ViteX.

Discord Set Up
-
1. Create a Discord Server
2. Create a discord bot
    a) https://https://discord.com/developers/applications

    b) Create a New Application and create a new bot
    
3.  - Create invite url
    - OAuth2 > Scopes check bot
    - OAuth2 > Permissions set permissions
    
    PERMISSIONS
    
    - Send Messages
    - Manage Messages
    - Read Message History
    - Attach Files
    - View Channels
    
4. Invite Bot in Channel
    -follow url in OAuth2 > Scopes
    

Bot Setup
-

1. CREATE VITE X WALLET

2. Add whitelisted tading pairs to Delegation
    - ensure these pairs match config.py whitelist 
3. Create Virtual Env
4. Clone Git Repo
5. pip install requirements.txt
6. Create config.json using sample_config.json
     Add only the trading pairs that are delegated to the whitelist
    CONFIG.JS
    ---------
    - "live": Live Trading
    - "interval": 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w
    - "testnet": "https://api.vitex.net/test"
    - "mainnet": "https://api.vitex.net",
    - "quote_currency": "USDT-000", "BTC-000","ETH-000"
    - "discord_token": "YOUR_DISCORD_TOKEN"
    - "discord_channel": "YOUR_DISCORD_CHANNEL"
    - "stoploss": Defined Stoploss in percent
    - "takeprofit" : Defined Takeprofit in percent
    - "status_updates": Defined notification time in minutes
    - "size": Order Size if dynamic_size is false
    - "dynamic_size": Determines size based on available funds
    - "vite_key": "YOUR_VITE_KEY"
    - "vite_secret": "YOUR_VITE_SECRET"
    - "viteconnect_address": "VITE_CONNECT_ADDRESS"     (optional: api requests that require address) (None as value)
    - "delegation_address": "VITE_DELEGATION_ADDRESS"   (optional: api requests that require address) (None as value)
    - "whitelist": SELECTED TRADING PAIRS DEFINED IN DELEGATION
        - PRE DEFINED WHITELIST FOR MOST ACCURATE PAIRS


7. (optional) Define Custom Strategy in Strategy.py 
    -A Bollingerband RSI strategy is used as and example

8. run python vitetrader.py


Bot Commands
------------

/menu : List of commands

/start - Start the Vite X Trader
/stop - Stop the bot

/balance - get account balances
/open - get open orders
/active - get all active positions
/pnl - get Profit and Loss for active postions

/whitelist : List of current trading pairs
/timeframes : List of time intervals

$ detail <TRADING_PAIR>  :  detail for a specific trading pair on ViteX
$ detail <SYMBOL>  :  detail for a specific currency on ViteX