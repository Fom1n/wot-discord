import discord

from src.province import create_view


class MessageMapper:

    async def mapMessage(self, msg):

        # let's ignore our own messages
        if msg.author.id == self.client.user.id:
            return
        if msg.content.startswith('>>provinces'):
            await msg.channel.send("Please select your options!", view=create_view())
            return
        if msg.content.startswith('>>') and not msg.author.guild_permissions.administrator:
            await msg.channel.send('I\'m sorry boy, but you can\'t do that here. Go ask pappa to do it.')
            return
        if msg.content.startswith('>>hello'):
            await msg.channel.send('Hi!')
        if msg.content.startswith('>>setclan'):
            await self.setClanHandler(msg)
        if msg.content.startswith('>>setchannel'):
            await self.setChannelHandler(msg)

    async def setChannelHandler(self, msg):
        arr = msg.content.split(" ")
        if len(arr) < 2 | len(arr) > 2:
            await msg.channel.send("You need to specify type of channel. Currently supported - **SH**, **PFP***")
            return
        channel_id = msg.channel.id
        guild_id = msg.author.guild.id
        channel_type = arr[1]
        if channel_type == "SH" or channel_type == "PFP":
            inserted = self.db_handler.updateChannel(guild_id, channel_id, arr[1])
            if inserted:
                await msg.channel.send(
                    "I've successfully saved the channel where you want me to spam " + arr[1] + " info "
                                                                                                "to.")
        else:
            await msg.channel.send("English, do you speak it? I don't know what you want me to do.")

    async def setClanHandler(self, msg):
        arr = msg.content.split(" ")
        if len(arr) < 2 | len(arr) > 2:
            await msg.channel.send("You need to specify clan after space, like this - '$setclan FAME' ")
            return
        else:
            clan_data = self.wg_api.get_clan_id(arr[1])
            # print(clan_data)
            if clan_data['status'] != "ok":
                await msg.channel.send("There is something wrong with the request. Please try again later.")
                return
            if int(clan_data['meta']['count']) != 1:
                await msg.channel.send("Sorry, I did not find your clan. Please check again.")
                return
            inserted = self.db_handler \
                .updateGuildClan(int(msg.author.guild.id), arr[1], self.get_clan_id(clan_data))
            if inserted:
                await msg.channel.send("Successfully updated your clan tag to [" + arr[1] + "]!")
                return
            else:
                await msg.channel.send("Could not update your clan tag for some reason. Please try again later.")
                return

    def get_clan_id(self, clan_data):
        print(int(clan_data['data'][0]['clan_id']))
        return int(clan_data['data'][0]['clan_id'])

    def __init__(self, client, db_handler, wg_api):
        self.client = client
        self.db_handler = db_handler
        self.wg_api = wg_api
        pass
