import interactions
import asyncio
import a2s
from datetime import datetime
import sys
from loguru import logger

import logging
#logging.basicConfig(level=logging.DEBUG)

TOKEN = "" #Your bot token
GUILD_ID = 0 #Right click your server icon and hit "Copy ID"
ADMINISTRATOR_ROLE_ID = 0 #Right click the role you want managing this bot and hit "Copy ID"

#Add servers here - shortname is displayed when the server cannot be contacted
servers = [
    {
        "ip": "209.236.114.122", #Avtomat
        "shortname": "Avtomat Events",
        "port": 27016,
        "flag": ":flag_us:",
        "extrainfo": {
            "ACF Version": "ACF3"
        }
    },
    {
        "ip": "209.236.114.122", #Malleus Gaming
        "shortname": "Malleus Gaming",
        "port": 27015,
        "flag": ":flag_us:",
        "extrainfo": {
            "ACF Version": "ACF3"
        }
    },
    {
        "ip": "31.186.250.16", #Cre8ive
        "shortname": "Cre8ive 4.0",
        "port": 27015,
        "flag": ":flag_de:",
        "extrainfo": {
            "ACF Version": "ACF3",
            "Notes": "No Starfall"
        }
    },
    {
        "ip": "185.107.96.6", #Real Builders
        "shortname": "Real Builders",
        "port": 27015,
        "flag": ":flag_de:",
        "extrainfo": {
            "ACF Version": "ACF3"
        }
    },
    {
        "ip": "116.202.240.95", #AWM Builders
        "shortname": "LUMOS Builder's Paradise",
        "port": 27045,
        "flag": ":flag_de:",
        "extrainfo": {
            "ACF Version": "ACF2 + ACF Custom"
        }
    },
    {
        "ip": "185.44.76.2", #AWM Builders
        "shortname": "AWM Builders 2.0",
        "port": 27115,
        "flag": ":flag_gb:",
        "extrainfo": {
            "ACF Version": "ACE"
        }
    }
]

bot = interactions.Client(token=TOKEN)

def curTime():
    return datetime.now().strftime("%Y-%m-%d %I:%M:%S%p")

embedFields = []

async def serverMonitor(msg):
    while True:
        embedFields.clear()

        #Exceptions in async functions seem to vanish into thin air without logging them manually
        try:
            for server in servers:
                data = None

                try:
                    data = await a2s.ainfo((server["ip"], server["port"]), 0.25)
                except asyncio.exceptions.TimeoutError:
                    pass
                except Exception as e:
                    logger.exception(e)

                nameStr = ""
                valueStr = "**Current player count:** N/A\n**Current map:** N/A"
                if data is not None:
                    nameStr = data.server_name
                    valueStr = ("steam://connect/" + server["ip"] + ":" + str(data.port) +
                        "\n**Current player count:** " + str(data.player_count) + "/" + str(data.max_players) + 
                        "\n**Current map:** " + data.map_name)
                else:
                    nameStr = server["shortname"] + " [NOT RESPONDING]"

                if "extrainfo" in server:
                    for name, value in server["extrainfo"].items():
                        valueStr = valueStr + "\n**" + name + ":** " + value

                embedFields.append(
                    interactions.EmbedField(
                        name = server["flag"] + " " + nameStr,
                        value = valueStr,
                        inline = False
                    )
                )

            embedFields.append(
                interactions.EmbedField(
                    name = "\u200b",
                    value = "Last updated at " + curTime() + " EST.",
                    inline = False
                )
            )

            embed = interactions.Embed(
                title = ":computer: Build Server List",
                description = "These are the servers that we've determined are decent for building on.",
                fields = embedFields
            )

            await msg.edit(content="\u200b", embeds=embed)
        except Exception as e:
            logging.exception(e)

        await asyncio.sleep(30)

tasks = {}

@bot.command(
    name="monitor",
    description="Begin monitoring servers in this channel",
    scope=GUILD_ID
)
async def monitor(ctx: interactions.CommandContext):
    if ADMINISTRATOR_ROLE_ID in ctx.author.roles:
        msg = await ctx.send(content="Beginning server monitoring...")

        if "main" in tasks:
            tasks["main"]["task"].cancel()
            await tasks["main"]["msg"].delete()

        tasks["main"] = {
            "task": asyncio.create_task(serverMonitor(msg)),
            "msg": msg
        }
    else:
        await ctx.send(content="You don't have permission to use this command.")

@bot.event
async def on_ready():
    logger.debug("Ready to begin monitoring!")

bot.start()
