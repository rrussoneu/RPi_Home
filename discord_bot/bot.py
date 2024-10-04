import os
import json
import discord
from discord.ext import commands
import paho.mqtt.client as paho
import asyncio
from bot_topics import *
import ssl

# Set up Discord bot
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
AUTHORIZED_USER = int(os.getenv('DISCORD_USER_ID')) 

# Need to enable these
intents = discord.Intents.default()
intents.messages = True  
intents.message_content = True  

# Prefix = ! for sending a command
bot = commands.Bot(command_prefix='!', intents=intents)

# MQTT config
MQTT_BROKER = os.getenv('MQTT_BROKER') 
MQTT_PORT = int(os.getenv('MQTT_PORT', '8883'))
MQTT_USERNAME = os.getenv('MQTT_USER')    
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')  

# Init MQTT client
mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(BOT_DOOR_LIGHT_ALERT)
        client.subscribe(BOT_LIVING_ROOM_TEMP_ALERT)
        
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}")

def on_message(client, userdata, msg):
    if msg.topic == BOT_DOOR_LIGHT_ALERT:
        alert_message = msg.payload.decode()
        print(f"Received alert: {alert_message}")
        asyncio.run_coroutine_threadsafe(send_alert(alert_message), bot.loop)
    elif msg.topic == BOT_LIVING_ROOM_TEMP_ALERT:
        alert_message = msg.payload.decode()
        print(f"Received alert: {alert_message}")
        asyncio.run_coroutine_threadsafe(send_alert(alert_message), bot.loop)


mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.loop_start()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot is online and ready for commands!")

@bot.command(name='light')
async def light_control(ctx, action: str):
    if ctx.author.id != AUTHORIZED_USER:
        await ctx.send("You are not authorized to use this command.")
        return
    
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("You cannot use this command in this channel.")
        return

    if action.lower() == 'on':
        mqtt_client.publish(BOT_DOOR_LIGHT_CONTROL, "turn on")
        await ctx.send("Light is being turned ON.")
    elif action.lower() == 'off':
        mqtt_client.publish(BOT_DOOR_LIGHT_CONTROL, "turn off")
        await ctx.send("Light is being turned OFF.")
    else:
        await ctx.send("Unknown command. Use `!light on` or `!light off`.")


@bot.command(name='fan')
async def light_control(ctx, action: str):
    if ctx.author.id != AUTHORIZED_USER:
        await ctx.send("You are not authorized to use this command.")
        return
    
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("You cannot use this command in this channel.")
        return

    if action.lower() == 'on':
        mqtt_client.publish(BOT_LIVING_ROOM_FAN_CONTROL, "turn on")
        await ctx.send("Light is being turned ON.")
    elif action.lower() == 'off':
        mqtt_client.publish(BOT_LIVING_ROOM_FAN_CONTROL, "turn off")
        await ctx.send("Light is being turned OFF.")
    else:
        await ctx.send("Unknown command. Use `!fan on` or `!fan off`.")

# Function to send an alert to the Discord channel
async def send_alert(message):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)



# Run the bot
bot.run(TOKEN)