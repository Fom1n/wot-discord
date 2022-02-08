import discord
from discord import Embed

from src.province import create_view
from src.region import create_region_view


class MessageMapper:

    async def mapMessage(self, msg):

        # All messages
        if msg.author.id == self.client.user.id:
            return
        embed = Embed(
            title="test"
        )
        embed.add_field(name="Test name", value="Test hyperlink [[tag]](https://stackoverflow.com) and another [one](https://www.youtube.com)")
        # await msg.channel.send("Trying embed", embed=embed)

        if msg.content.startswith(">>region") and msg.author.guild_permissions.administrator:
            await msg.channel.send("Please select your region.", view=create_region_view(self.db_handler))
            return
        # Check for region
        region_exists, region = self.check_region(msg)
        if msg.content.startswith('>>') and not region_exists:
            reg_view = None
            if msg.author.guild_permissions.administrator:
                reg_view = create_region_view(self.db_handler)
            await msg.channel.send("You need to select region first.", view=reg_view)
            return

        if msg.content.startswith('>>provinces'):
            if region == 'ru':
                await msg.channel.send(ru['province'], view=create_view(region))
            else:
                await msg.channel.send(eu['province'], view=create_view(region))
            return
        # Admin messages
        if msg.content.startswith('>>') and not msg.author.guild_permissions.administrator:
            await msg.channel.send('I\'m sorry boy, but you can\'t do that here. Go ask pappa to do it.')
            return
        if msg.content.startswith('>>deletechannel'):
            self.delete_channel_handler(msg)
            await msg.channel.send(":white_check_mark:")

        if msg.content.startswith('>>setchannel'):
            await self.setChannelHandler(msg)

    def check_region(self, msg):
        region = self.db_handler.getRegion(msg.guild.id)
        if region is None:
            return False, region
        return True, region

    def delete_channel_handler(self, msg):
        guild_id = msg.author.guild.id
        channel_id = msg.channel.id
        self.db_handler.delete_channel(channel_id, guild_id)

    async def setChannelHandler(self, msg):
        arr = msg.content.split(" ")
        if len(arr) < 4 | len(arr) > 4:
            await msg.channel.send("WRONG MSG. Example - >>setchannel PFP MERCY ru")
            return
        channel_id = msg.channel.id
        guild_id = msg.author.guild.id
        channel_type = arr[1]
        clan = arr[2]
        region = arr[3]
        if region != 'ru' and region != 'eu':
            await msg.channel.send("Region must be either ru or eu (lower case)")
        if channel_type == "PFP":
            inserted = self.db_handler.updateChannel(guild_id, channel_id, channel_type, clan, region)
            if inserted:
                await msg.channel.send(
                    "I've successfully saved the channel where you want me to spam " + arr[1] + " info "
                                                                                                "to.")
        elif channel_type == "BAT":
            await self.set_clan(clan, region, msg.channel)
            inserted = self.db_handler.updateChannel(guild_id, channel_id, channel_type, clan, region)
            if inserted:
                await msg.channel.send(
                    "I've successfully saved the channel where you want me to spam battles info to.")
        else:
            await msg.channel.send("None")

    async def set_clan(self, clan_tag, region, channel):
        # print(clan_data)

        exists = self.db_handler.clan_name_and_id_exists(clan_tag, region)
        if exists:
            return
        else:
            clan_data = self.wg_api.get_clan_id(clan_tag, region)
            if clan_data['status'] != "ok":
                await channel.send("There is something wrong with the request. Please try again later.")
                return
            if int(clan_data['meta']['count']) != 1:
                await channel.send("Either no clan is found, or more than one. Give me your exact clan tag.")
                return
            clan_id = self.get_clan_id(clan_data)
            self.db_handler.insert_clan_name_and_id(clan_tag, clan_id, region)

    def get_clan_id(self, clan_data):
        return int(clan_data['data'][0]['clan_id'])

    def __init__(self, client, db_handler, wg_api):
        self.client = client
        self.db_handler = db_handler
        self.wg_api = wg_api
        pass

ru = {
    'province': "Выберите опции для отображения провинций"
}

eu = {
    'province': "Select options to display provinces (select one of the maps None, discord select menu limitation)"
}