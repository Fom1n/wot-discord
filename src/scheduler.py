import asyncio

import discord
from discord import Embed

from src.province import is_none, map_to_picture, inv_maps


class Scheduler:

    async def schedule_bat_update(self):
        channels = self.db_handler.getChannelsAndClansInfo("BAT")
        if len(channels) == 0:
            print("No BAT channel set")
        for channel in channels:
            guild_id = channel[0]
            channel_id = channel[1]
            channel_type = channel[2]
            clan = channel[3]
            region = channel[4]
            channel = discord.utils.get(self.client.get_all_channels(), id=channel_id)

            clan_id = self.db_handler.get_clan_name_and_id(clan, region)
            if len(clan_id) == 0:
                continue
            clan_id = clan_id[0][1]
            if channel_type != 'BAT':
                continue
            battles = self.wg_api.get_global_map_battles_info(clan_id, region)
            planned = battles['planned_battles']
            scheduled = battles['battles']
            embeds, files = self.generate_embeds_planned(planned, region)
            for i, embed in enumerate(embeds):
                file = files[i]
                await channel.send(embed=embed, file=file)


    def generate_embeds_planned(self, planned, region):
        embeds = []
        files = []
        for battle in planned:
            province_id = battle['province_id']
            embed = Embed(
                color=discord.Color.gold(),
                title=region_map[region]['planned_embed'] + battle['province_name'],
                url=region_map[region]['province_base_url'] + battle['province_id']
            )
            prime = self.prime_to_local(battle['battle_time'], region)
            embed.add_field(
                name=region_map[region]['prime_embed'], value=prime, inline=True)
            self.handle_is_attacker(embed, battle['is_attacker'], region)
            embed.add_field(name=region_map[region]['respawn_embed'], value=battle['arena_resp_number'], inline=True)
            self.handle_single_clan(battle['province_owner_id'], embed, region, 'owner_embed')
            self.handle_single_clan(battle['enemy'], embed, region, 'enemy_embed')
            embed.add_field(name=region_map[region]['server_embed'], value=battle['periphery'], inline=False)
            embed.add_field(
                name=region_map[region]['front_embed'], value=region_map[region]['fronts_inv'][battle['front_id']],
                inline=True)
            embeds.append(embed)
            embed.set_thumbnail(
                url="attachment://map.png")

            file = discord.File(map_to_picture[battle['arena_name']], filename="map.png")
            files.append(file)
        return embeds, files




    def handle_single_clan(self, clan_id, embed, region, clan_type):
        if is_none(clan_id):
            embed.add_field(
                name=region_map[region][clan_type],
                value="---------"
            )
            return
        string = ""
        clan_info_gm = self.wg_api.get_clan_global_map_info(str(clan_id), region)
        clan_info_general = self.wg_api.get_clan_info(clan_id, region)
        global_map_elo = clan_info_gm['gm_elo_rating_10']
        clan_tag = clan_info_general['clanview']['clan']['tag']
        string = string + "[[" + clan_tag + "]](" + region_map[region]['clan_base_url'] + str(clan_id) + \
                 ") - Elo = " + str(global_map_elo) + "\n"
        embed.add_field(
            name=region_map[region]['owner_embed'],
            value=string
        )

    def handle_is_attacker(self, embed, is_attacker, region):
        if is_attacker:
            embed.add_field(name=region_map[region]['attacker_embed'], value="✅", inline=True)
        else:
            embed.add_field(name=region_map[region]['attacker_embed'], value="❎", inline=True)

    def prime_to_local(self, prime, region):
        time = str(prime).split(" ")[1]
        time_arr = time.split(':')
        if region == 'eu':
            time_arr[0] = str(int(time_arr[0]) + 1)
            return time[0] + " " + ':'.join(time_arr)
        else:
            time_arr[0] = str(int(time_arr[0]) + 3)
            return time[0] + " " + ':'.join(time_arr)

    async def schedule_pfp_update(self):
        channels = self.db_handler.getChannelsAndClansInfo("PFP")
        if len(channels) == 0:
            print("No pfp channel set")
        # break
        for channel in channels:
            guild_id = channel[0]
            channel_id = channel[1]
            channel_type = channel[2]
            clan = channel[3]
            region = channel[4]
            if channel_type != 'PFP':
                continue
            channel = discord.utils.get(self.client.get_all_channels(), id=channel_id)
            if channel is None:
                continue
            try:
                ratings = self.wg_api.get_player_fame_details(clan, region)['accounts_ratings']
            except Exception as e:
                print(e)
                continue
            filtered = map(lambda x: {
                'name': x['name'],
                'fame_points': x['fame_points'],
                'rewards': x['rewards'],
                'rank': x['rank']
            }, ratings)
            sorted_info = sorted(filtered, key=lambda d: d['fame_points'], reverse=True)
            message = "```"
            messages = []
            for i, player in enumerate(sorted_info):
                player_place = player['rank']
                fame_points = player['fame_points']
                rewards = player['rewards']
                name = player['name']
                message += ""
                tank = "[🔴]"
                styles = "[🔴]"
                for data in rewards:
                    if data['reward_type'] == "styles":
                        styles = "[🟢]"
                    if data['reward_type'] == "tank_availability":
                        tank = "[🟢]"
                message += region_map[region]['tank'] + tank + ", " + region_map[region]['style'] + styles + ", " + \
                           region_map[region]['fame'] + str(fame_points)
                fame_diff = 5 - len(str(fame_points))
                for j in range(fame_diff):
                    message += ' '
                message += " " + region_map[region]['name'] + name + "\n"
                if i % 10 == 0 and i != 0:
                    message += "```"
                    messages.append(message)
                    message = "```"
            message += "```"
            messages.append(message)

            await self.clear(channel)
            for message in messages:
                await channel.send(message)

    async def sh_before(self):
        await self.client.wait_until_ready()

    async def fp_before(self):
        await self.client.wait_until_ready()

    def check_region(self, guild_id):
        region = self.db_handler.getRegion(guild_id)
        if region is None:
            return False, region
        return True, region

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
        mgs = await channel.history(limit=10).flatten()
        await channel.delete_messages(mgs)

    def send_sh_message(self):
        pass

    def __init__(self, client, db_handler, msg_mapper, wg_api, clan_utils):
        self.db_handler = db_handler
        self.msg_mapper = msg_mapper
        self.wg_api = wg_api
        self.client = client
        self.clan_utils = clan_utils

fronts_eu = {
    'Basic': "confrontation_eu_league1",
    'Advanced': "confrontation_eu_league2",
    'Elite': "confrontation_eu_league3"
}

fronts_ru = {
    'Базовый': "confrontation_ru_league1",
    'Продвинутый': "confrontation_ru_league2",
    'Элитный': "confrontation_ru_league3"
}

fronts_eu_inv = {v: k for k, v in fronts_eu.items()}
fronts_ru_inv = {v: k for k, v in fronts_ru.items()}

ru = {
    'tank': "Танк: ",
    'fame': "Очки славы: ",
    'place': "Место: ",
    'style': "3д стиль: ",
    'name': "Ник: ",
    'province_base_url': "https://ru.wargaming.net/globalmap/#province/",
    'clan_base_url': "https://ru.wargaming.net/clans/wot",
    'planned_embed': "Запланированный: ",
    'prime_embed': "Прайм Тайм (МСК)",
    'map_embed': "Карта",
    'server_embed': "Сервер",
    'min_bet_embed': "Минимальная ставка",
    'last_won_bet_embed': "Последняя выигрышная ставка",
    'front_embed': "Фронт",
    'owner_embed': "Владелец",
    'attackers_embed': "Атакующие кланы",
    'competitors_embed': "Турнирные кланы",
    'bonus_embed': "Бонусы провинции",
    'length': "Количество кланов - ",
    'attacker_embed': "Мы атакуем?",
    'respawn_embed': "Респавн",
    'enemy_embed': "Противник",
    'fronts': fronts_ru,
    'fronts_inv': fronts_ru_inv,
}

eu = {
    'tank': "Tank: ",
    'fame': "Fame points: ",
    'place': "Place: ",
    'style': "3d style: ",
    'name': "Player name: ",
    'province_base_url': "https://eu.wargaming.net/globalmap/#province/",
    'clan_base_url': "https://eu.wargaming.net/clans/wot/",
    'planned_embed': "Planned: ",
    'prime_embed': "Prime time (CET)",
    'map_embed': "Map",
    'server_embed': "Server",
    'min_bet_embed': "Minimum bet",
    'last_won_bet_embed': "Last won bet",
    'front_embed': "Front",
    'owner_embed': "Province owner",
    'attackers_embed': "Attackers clans",
    'competitors_embed': "Competitors clans",
    'bonus_embed': "Province bonuses",
    'length': "Number of clans - ",
    'attacker_embed': "We attac?",
    'respawn_embed': "Respawn",
    'enemy_embed': "Enemy",
    'fronts': fronts_eu,
    'fronts_inv': fronts_eu_inv,
}

region_map = {
    'ru': ru,
    'eu': eu
}
