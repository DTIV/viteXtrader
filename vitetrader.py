from requests import get, post
import discord
from discord.ext import tasks
import json
import functions as fn
import messages as msg
from main import main
import orders as ordr
from datetime import datetime
'''
############################

     VITE X TRADER
     
###########################


LIMIT ORDERS CURRENTLY NOT FUNCTIONING:
HMAC SHA256 SIGNATURE
'''
#Read Config
f = open("config.json")
config = json.load(f)

#Start Discord Client
client = discord.Client()
channel_id = int(config['discord_channel'])

#Settings
interval = fn.sort_interval(config['interval'])
cache = {}
status_updates = config['status_updates']
whitelist = config['whitelist']

cache = {}
for symbol in whitelist:
    cache[symbol] = {
        'data' : {
            'active': False,
            'message': None
            }
        }

@client.event
async def on_ready():
    notifications.start()
    channel = client.get_channel(channel_id)   
    await channel.send(msg.startup_msg())

@tasks.loop(minutes=interval)
async def trader():
    channel = client.get_channel(channel_id)
    main(cache)
    for i in cache:
        if cache[i]['data']['message'] != None:
            await channel.send(cache[i]['data']['message'])
            cache[i]['data']['message'] = None
    await channel.send(f"Still Searching {config['interval']} Candles -- {str(datetime.now()).split('.')[0]}")

@tasks.loop(minutes=status_updates)
async def notifications():
    channel = client.get_channel(channel_id)
    await channel.send("Bot is Listening.....")

@client.event
async def on_message(message):
    mc = message.content
    pair = ""
    if message.author == client.user:
        return
    if '/' in mc[0]:
        if mc.startswith('/menu'):
            await message.channel.send(msg.menu_msg())
        if mc.startswith('/timeframes'):
            await message.channel.send(msg.timeframe_msg())
        if mc.startswith('/start'):
            await message.channel.send("Vite X Trader Starting Up! ... ")
            trader.start()
            await message.channel.send("BOT STARTED!")
        if mc.startswith('/stop'):
            trader.stop()
            notifications.stop()
            await message.channel.send("BOT STOPPED!")
        if mc.startswith('/whitelist'):
            await message.channel.send(msg.get_whitelist())
        if mc.startswith('/balance'):
            await message.channel.send(ordr.get_balance())
        if mc.startswith('/open'):
            await message.channel.send(ordr.get_open_orders())
        if mc.startswith('/active'):
            await message.channel.send('\n'.join(ordr.get_active_positions(cache)))
        if mc.startswith('/pnl'):
            await message.channel.send(ordr.get_pnl(cache))
    
    if '$' in mc[0]:
        a, symbol_list = fn.get_all_tokens()
        for tp in whitelist:
            if mc.startswith('$'+" detail "+tp):
                pair = tp
        if mc.startswith('$'+" detail"):
             sec_command = mc.split("$ detail",1)[1].replace(" ","")
             if sec_command in symbol_list:
                 await message.channel.send(msg.get_token_detail(sec_command))

    if pair:
        sec_command = mc.split("$ detail",1)[1].replace(" ","")
        if sec_command == pair:
            await message.channel.send(msg.pair_info_msg(pair))
        
        
try:
    client.run(config['discord_token'])
except KeyboardInterrupt():
    print("Bot stopped")