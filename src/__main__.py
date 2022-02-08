# bot.py
import asyncio
import os
import threading

import discord
from discord.ext import tasks

from dotenv import load_dotenv

from clanutils import clanUtils
from dbHandler import DbHandler
from msgMapper import MessageMapper
from scheduler import Scheduler
from wgApi import wgApi

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
clan_utils = clanUtils()
client = discord.Client(intents=intents)

db_handler = DbHandler()
wg_api = wgApi()
mapper = MessageMapper(client, db_handler, wg_api)

scheduler = Scheduler(client, db_handler, mapper, wg_api, clan_utils)


@client.event
async def on_ready():
    autoupdate.start()


@tasks.loop(hours=1)
async def autoupdate():
    # await scheduler.schedule_sh_update()
    await scheduler.schedule_pfp_update()
    # await scheduler.schedule_bat_update()

@autoupdate.before_loop
async def before():
    await client.wait_until_ready()
#
#
@client.event
async def on_message(message):
    # print(message.author.guild_permissions.administrator)
    # mapper.mapMessage(message)
    await mapper.mapMessage(message)


client.run(TOKEN)


def main():
    print("work")


if __name__ == "__main__":
    main()
