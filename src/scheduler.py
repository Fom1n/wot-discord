import asyncio

import discord


class Scheduler:

    async def schedule_sh_update(self):
        channels = self.db_handler.getClanAndChannel("SH")
        if len(channels) == 0:
            print("No pfp channel set")
        # break
        val = channels[0]
        channel_id = val[2]
        channel = discord.utils.get(self.client.get_all_channels(), id=channel_id)

        guild_id = val[0]
        region_check, region = self.check_region(guild_id)
        if not region_check:
            await channel.send("No region specified")

        clan_info = self.db_handler.getClanIds(val[0])

        clan_id = clan_info[2]
        clan_name = clan_info[1]

        sh_info = self.wg_api.get_clan_sh_info(clan_id, region)
        sh_ten_wr = self.clan_utils.calculate_sh_10_winrate(sh_info, clan_id)

        embed = self.generate_embed_sh(sh_ten_wr, clan_name)

        await self.clear(channel)
        # await channel.send(embed=embed)

    async def sh_before(self):
        await self.client.wait_until_ready()

    async def fp_before(self):
        await self.client.wait_until_ready()

    def check_region(self, guild_id):
        region = self.db_handler.getRegion(guild_id)
        if region is None:
            return False, region
        return True, region

    async def schedule_players_fame_points_update(self):
        channels = self.db_handler.getClanAndChannel("PFP")
        if len(channels) == 0:
            print("No pfp channel set")
        # break
        val = channels[0]
        channel_id = val[2]
        channel = discord.utils.get(self.client.get_all_channels(), id=channel_id)
        guild_id = val[0]
        region_check, region = self.check_region(guild_id)
        if not region_check:
            await channel.send("No region specified")
        await channel.send("=========== Latest data below ===========")

        clan_info = self.db_handler.getClanIds(guild_id)

        clan_id = clan_info[2]

        clan_details = self.wg_api.get_clan_details(clan_id, region)
        player_ids = self.clan_utils.get_player_ids(clan_details, clan_id)
        player_names = self.clan_utils.get_player_names(clan_details, clan_id)

        player_names_and_ids = dict(zip(player_ids, player_names))
        player_fame_array = []

        messages = []
        message = "```"
        for i, id in enumerate(player_ids):
            print(i)
            # if i == 5:
            #     break
            try:
                player_fame = self.wg_api.get_player_fame_details(id, region)['data'][str(id)]['events']['thunderstorm'][0]
                print(player_fame)
            except Exception as e:
                continue
            # await asyncio.sleep(5)
            if player_fame['award_level'] is not None:
                player_fame_array.append(player_fame)
        print(len(player_fame_array))
        player_fame_array = sorted(player_fame_array, key=lambda d: int(d['award_level']))
        print(len(player_fame_array))
        for i, fame_info in enumerate(player_fame_array):
            print(fame_info['award_level'])
            player_place = fame_info['award_level']

            fame_points = fame_info['fame_points']
            if int(player_place) < 4000:
                message += "🟢"
            else:
                message += "🔴"
            player_name = player_names_and_ids[int(fame_info['account_id'])]
            message += str(player_name)

            player_name_length = len(str(player_name))
            player_name_diff = 25 - player_name_length

            for j in range(player_name_diff):
                message += ' '

            message += ": Place - " + str(player_place) + ", Fame points - " + str(fame_points) + "\n"
            # print(message)
            if i % 10 == 0 and i != 0:
                print("appending to array")
                message += "```"
                messages.append(message)
                message = "```"
        print(len(messages))
        if len(messages) == 0:
            message += "```"
            await channel.send(message)
        for i, msg in enumerate(messages):
            print(i)
            await channel.send(msg)

    def generate_embed_sh(self, adv_wr, clan_name):
        embed = discord.Embed(
            title="SH statistics for clan [" + clan_name + "]",
            description="There's some stronghold statistics for your clan. Enjoy :face_with_monocle: ",
            color=discord.Color.purple()
        )
        embed.add_field(name="**Tier 10 SH winrate**", value=adv_wr)
        embed.set_footer(text="just get better lol")
        return embed

    async def clear(self, channel):
        mgs = await channel.history(limit=1).flatten()
        await channel.delete_messages(mgs)

    def send_sh_message(self):
        pass

    def __init__(self, client, db_handler, msg_mapper, wg_api, clan_utils):
        self.db_handler = db_handler
        self.msg_mapper = msg_mapper
        self.wg_api = wg_api
        self.client = client
        self.clan_utils = clan_utils
