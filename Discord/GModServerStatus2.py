import discord
from discord.ext import commands
import asyncio
import math
import requests
from datetime import datetime

bot = commands.Bot(command_prefix="%", help_command=None)
TOKEN = "YOUR_TOKEN"
servers = {
    "646366": { #ID of the server on trackyserver.com
        "name": "Avtomat Events Build & Practice", #Display name of the server
        "flag": ":flag_us:" #Location flag that will display next to the server name
    },
    "655993": {
        "name": "Malleus Gaming Sandbox",
        "flag": ":flag_us:"
    },
    "608767": {
        "name": "Cre8ive 4.0",
        "flag": ":flag_de:"
    },
    "75842": {
        "name": "Real Builders - 500+ Hours",
        "flag": ":flag_de:"
    },
    "627338": {
        "name": "[LUMOS] Builder's Paradise",
        "flag": ":flag_gb:"
    }
}

def curTime():
    return datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

def log(msg):
    print("[" + curTime() + "] " + msg)

@bot.event
async def on_ready():
    log(f"We have logged in as {bot.user}")
    game = discord.Game(f"Monitoring {len(servers)} servers | %monitor to begin monitoring")
    await bot.change_presence(status=discord.Status.online, activity=game)

def generateServerStatusEmbed():
    embed = discord.Embed(title=":computer: Build Server List", description="These are the servers that we've determined are decent for building & testing on.")
    
    count = 0

    for id, data in servers.items():
        try:
            req = requests.get("https://api.trackyserver.com/widget/index.php?id=" + id).json()
            if req["playerscount"] == "offline":
                req["map"] = "N/A"
            embed.add_field(name=data["flag"] + " " + data["name"] + " (" + req["playerscount"] + ") - " + req["map"], value="steam://connect/" + req["ip"], inline=False)
            
            count = count + 1
        except:
            log(f"Failed to get JSON data for server {id} ({data['name']})")

    if count == 0:
        embed.add_field(name="\u200b", value="*No servers defined, or problem contacting api.trackyserver.com*", inline=False)

    embed.add_field(name="\u200b", value="Last updated at " + curTime() + " EST")
    return embed

async def serverMonitor(ctx):
    #Delete command message, and message before if said message was by the monitor bot
    await ctx.message.delete()
    async for message in ctx.channel.history(limit=1):
        if message.author == bot.user:
            await message.delete()

    msg = await ctx.send(embed=generateServerStatusEmbed())

    while True:
        await asyncio.sleep(300)
        await msg.edit(embed=generateServerStatusEmbed())

tasks = {}
@bot.command()
@commands.has_guild_permissions(administrator=True)
async def monitor(ctx):
    if "main" in tasks: #If we monitor in a new channel, stop the task monitoring in the old one
        tasks["main"].cancel()
    tasks["main"] = asyncio.create_task(serverMonitor(ctx))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(str(error))
        log(str(error))
    else:
        log(str(error))

bot.run(TOKEN)
