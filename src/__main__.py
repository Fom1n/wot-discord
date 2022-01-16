# bot.py
import os

import discord

from dotenv import load_dotenv

from dbHandler import DbHandler
from msgMapper import MessageMapper


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

db_handler = DbHandler()
mapper = MessageMapper(client, db_handler)


@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(client.guilds)
    print(
        f'{client.user.id} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@client.event
async def on_message(message):
    print(message)
    # mapper.mapMessage(message)

    await mapper.mapMessage(message)


client.run(TOKEN)


def main():
    print("work");


if __name__ == "__main__":
    main()