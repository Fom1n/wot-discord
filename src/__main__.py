# bot.py
import os

import discord

from dotenv import load_dotenv
from msgMapper import MessageMapper


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

mapper = MessageMapper(client)


@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@client.event
async def on_message(message):
    # print(message.content)
    # mapper.mapMessage(message)

    await mapper.mapMessage(message)


client.run(TOKEN)


def main():
    print("work");


if __name__ == "__main__":
    main()