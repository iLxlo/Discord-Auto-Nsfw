import os
import discord
import requests
import asyncio
import random
import configparser
from discord.ui import View, Button
from discord.ext import commands
from colorama import Fore, Style, init
import logging
from colored import fg, attr

config = configparser.ConfigParser()
config.read("./data/config.ini")

nekobot_api_key = config["Nekobot"]["api_key"]
discord_token = config["Discord"]["token"]
channel_id = config["Discord"]["channel"]
prefix = config["Discord"]["prefix"]
auth_url = config["Auth"]["URL"]

intents = discord.Intents.all()

client = commands.Bot(config["Discord"]["prefix"], intents=intents)

@client.event
async def on_ready():
    cogs_to_load = ["cogs.set", "cogs.del", "cogs.greeter", "cogs.embed", "cogs.unban"]

    os.system("cls" if os.name == "nt" else "clear")  # Use cls for Windows, clear for other systems

    a = fg("#babaf8")
    b = fg("#7c7cf8")
    c = fg("#3e3ef8")
    r = attr(0)

    username = client.user.name
    version = "1.0"  # Replace with your actual version

    print(f"""
        {a} ____ _  _ ___ ____    _  _ ____ ____ _ _ _ 
        {b}|__| |  |  |  |  |    |\\ | [__  |___ | | | 
        {c}|  | |__|  |  |__|    | \\| ___] |    |_|_| 
    """ + r)
    print(f"{a}---------------------------------------------------------------" + f"{c} Made by iLxlo " + f"{a}---------------------------------------------------------------")
    print(f"""
        {c} Logged in as: {username}
        {a} Version: {version}
    """ + r)
    #command status
    for cog in cogs_to_load:
        try:
            await client.load_extension(cog)
            print(f"{c} Successfully loaded {cog} cog")
        except Exception as e:
            print(f"Failed to load {cog} cog. Error: {e}")

token = discord_token
client.run(token)

