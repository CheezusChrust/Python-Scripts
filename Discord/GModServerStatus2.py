import discord
from discord.ext import commands
import asyncio
import math
import requests
from datetime import datetime

bot = commands.Bot(command_prefix="%", help_command=None)
TOKEN = "YOUR-TOKEN-HERE"
servers = {
    "646366": {
        "name": "Avtomat Events Build & Practice",
        "flag": ":flag_us:"
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

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    game = discord.Game("%help for info")
    await bot.change_presence(status=discord.Status.online, activity=game)

@bot.command()
async def help(ctx):
    commands = [
        "**%ping** - Display the bot's current ping",
        "**%help** - Display this help message",
        "**%monitor** - Monitor servers in this channel (Admin only)"
    ]
    embed = discord.Embed(title=":information_source: Information", description="\n".join(commands), color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    embed = discord.Embed(title=":computer: Websocket Latency: " + str(math.floor(bot.latency * 1000)) + "ms", color=0x00ff00)
    await ctx.send(embed=embed)

def generateServerStatusEmbed():
    embed = discord.Embed(title=":computer: Build Server List", description="These are the servers that we've determined are decent for building & testing on.")
    try:
        for id, data in servers.items():
            req = requests.get("https://api.trackyserver.com/widget/index.php?id=" + id).json()
            if req["playerscount"] == "offline":
                req["map"] = "N/A"
            embed.add_field(name=data["flag"] + " " + data["name"] + " (" + req["playerscount"] + ") - " + req["map"], value="steam://connect/" + req["ip"], inline=False)
    except:
        print("[" + datetime.now().strftime("%I:%M:%S%p") + "] Error contacting api.trackyserver.com")
        embed.add_field(name="\u200b", value="*Error contacting api.trackyserver.com*", inline=False)
    embed.add_field(name="\u200b", value="Last updated at " + datetime.now().strftime("%I:%M:%S%p") + " EST")
    return embed

tasks = {}

#1. If message in channel, delete it
#2. Post status message
#3. Edit status message with updates every few minutes
async def serverMonitor(ctx):
    async for message in ctx.channel.history(limit=2):
        await message.delete()

    msg = await ctx.send(embed=generateServerStatusEmbed())

    while True:
        await asyncio.sleep(120)
        await msg.edit(embed=generateServerStatusEmbed())

@bot.command()
@commands.has_guild_permissions(administrator=True)
async def monitor(ctx):
    if "main" in tasks:
        tasks["main"].cancel()
    tasks["main"] = asyncio.create_task(serverMonitor(ctx))

#Error handling
@bot.event
async def on_command_error(ctx, error):
    time = "[" + datetime.now().strftime("%I:%M:%S%p") + "] "

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(str(error))
        print(time + str(error))
    else:
        print(time + str(error))

bot.run(TOKEN)
