from requests import get, post
import discord
from discord.ext import tasks
import json
import functions as fn
import messages as msg
from main import main
import orders as ordr
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

@client.event
async def on_ready():
    updater.start()
    channel = client.get_channel(channel_id)   
    await channel.send(msg.startup_msg())


@tasks.loop(minutes=interval)
async def trader():
    channel = client.get_channel(channel_id)
    main_object = main(cache)
    for i in main_object:
        if main_object[i]['data']['message']:
            await channel.send(main_object[i]['data']['message'])
    await channel.send(f"Still Searching {config['interval']} Candles")

@tasks.loop(minutes=status_updates)
async def updater():
    channel = client.get_channel(channel_id)
    await channel.send("Bot is Listening.....")

@client.event
async def on_message(message):
    mc = message.content
    if message.author == client.user:
        return
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
        updater.stop()
        await message.channel.send("BOT STOPPED!")
    if mc.startswith('/whitelist'):
        await message.channel.send(msg.get_whitelist())
    if mc.startswith('/balance'):
        await message.channel.send(ordr.get_balance(config['viteconnect_address']))
        
try:
    client.run(config['discord_token'])
except KeyboardInterrupt():
    print("Bot stopped")