import math

import discord
from discord import Embed

from src.province import map_to_picture, is_none


async def bat_display(db_handler, wg_api, discord_channel, clan, region, selector=None):
    clan_id = db_handler.get_clan_name_and_id(clan, region)
    if len(clan_id) == 0:
        return
    clan_id = clan_id[0][1]
    battles = wg_api.get_global_map_battles_info(clan_id, region)
    planned = battles['planned_battles']
    planned = sorted(planned, key=lambda d: d['battle_time'])
    scheduled = battles['battles']
    scheduled = sorted(scheduled, key=lambda d: d['battle_time'])
    if selector == 1 or selector is None:
        embeds, files = generate_embeds(wg_api, planned, region, "planned_embed")
        for i, embed in enumerate(embeds):
            file = files[i]
            await discord_channel.send(embed=embed, file=file)
    if selector == 2 or selector is None:
        embeds, files = generate_embeds(wg_api, scheduled, region, "battles_embed")
        for i, embed in enumerate(embeds):
            file = files[i]
            await discord_channel.send(embed=embed, file=file)


def generate_embeds(wg_api, planned, region, bat_type):
    embeds = []
    files = []
    for battle in planned:
        province_id = battle['province_id']

        embed = Embed(
            color=discord.Color.gold(),
            title=region_map[region][bat_type] + battle['province_name'],
            url=region_map[region]['province_base_url'] + battle['province_id']
        )
        prime = prime_to_local(battle['battle_time'], region)
        embed.add_field(
            name=region_map[region]['prime_embed'], value=prime, inline=True)
        handle_is_attacker(embed, battle['is_attacker'], region)
        embed.add_field(name=region_map[region]['respawn_embed'], value=battle['arena_resp_number'], inline=True)
        handle_single_clan(wg_api, battle['province_owner_id'], embed, region, 'owner_embed')
        handle_enemy(embed, region, battle['enemy'])
        embed.add_field(name=region_map[region]['server_embed'], value=battle['periphery'], inline=False)
        embed.add_field(
            name=region_map[region]['front_embed'], value=region_map[region]['fronts_inv'][battle['front_id']],
            inline=True)
        if type == "planned_embed":
            province_battles = wg_api.get_tournament_info(province_id, region)
            handle_pretenders(province_battles, region, embed)
        embeds.append(embed)
        embed.set_thumbnail(
            url="attachment://map.png")

        file = discord.File(map_to_picture[battle['arena_name']], filename="map.png")
        files.append(file)
    return embeds, files


def handle_enemy(embed, region, enemy):
    if is_none(enemy):
        embed.add_field(
            name=region_map[region]['enemy_embed'],
            value="---------"
        )
        return
    string = ""
    global_map_elo = enemy['elo_rating_10']
    clan_tag = enemy['tag']
    clan_id = enemy['id']
    string = string + "[[" + clan_tag + "]](" + region_map[region]['clan_base_url'] + str(clan_id) + \
             ") - Elo = " + str(global_map_elo) + "\n"
    embed.add_field(
        name=region_map[region]['enemy_embed'],
        value=string
    )


def handle_pretenders(battles, region, embed):
    pretenders = battles['pretenders']
    pretenders = sorted(pretenders, key=lambda d: d['elo_rating'], reverse=True)
    if len(pretenders) == 0:
        embed.add_field(
            name=region_map[region]['pretenders'],
            value="---------", inline=False)
    elif len(pretenders) <= 10:
        embed.add_field(
            name=region_map[region]['pretenders'] + ", " + region_map[region]['length'] + str(len(pretenders)),
            value=generate_clans_string(pretenders, region), inline=False)
    elif len(pretenders) > 10:
        three = math.floor(len(pretenders) / 3)
        embed.add_field(
            name=region_map[region]['pretenders'] + ", " + region_map[region]['length'] + str(len(pretenders)),
            value=generate_clans_string(pretenders[:three], region), inline=False)
        embed.add_field(
            name=region_map[region]['pretenders'] + ", " + region_map[region]['length'] + str(len(pretenders)),
            value=generate_clans_string(pretenders[three:three * 2], region), inline=False)
        embed.add_field(
            name=region_map[region]['pretenders'] + ", " + region_map[region]['length'] + str(len(pretenders)),
            value=generate_clans_string(pretenders[three * 2:], region), inline=False)


def generate_clans_string(clans, region):
    string = ""
    for clan in clans:
        global_map_elo = clan['elo_rating']
        clan_tag = clan['tag']
        clan_id = clan['id']
        string = string + "[[" + clan_tag + "]](" + region_map[region]['clan_base_url'] + str(clan_id) + \
                 ") - Elo = " + str(global_map_elo) + "\n"
    return string


def handle_single_clan(wg_api, clan_id, embed, region, clan_type):
    if is_none(clan_id):
        embed.add_field(
            name=region_map[region][clan_type],
            value="---------"
        )
        return
    string = ""
    clan_info_gm = wg_api.get_clan_global_map_info(str(clan_id), region)
    clan_info_general = wg_api.get_clan_info(clan_id, region)
    global_map_elo = clan_info_gm['gm_elo_rating_10']
    clan_tag = clan_info_general['clanview']['clan']['tag']
    string = string + "[[" + clan_tag + "]](" + region_map[region]['clan_base_url'] + str(clan_id) + \
             ") - Elo = " + str(global_map_elo) + "\n"
    embed.add_field(
        name=region_map[region][clan_type],
        value=string
    )


def handle_is_attacker(embed, is_attacker, region):
    if is_attacker:
        embed.add_field(name=region_map[region]['attacker_embed'], value="🔴", inline=True)
    else:
        embed.add_field(name=region_map[region]['attacker_embed'], value="🟢", inline=True)


def prime_to_local(prime, region):
    time = str(prime).split(" ")
    time_arr = time[1].split(':')
    time_arr.pop(-1)
    if region == 'eu':
        time_arr[0] = str(int(time_arr[0]) + 1)
        return time[0] + " " + ':'.join(time_arr)
    else:
        time_arr[0] = str(int(time_arr[0]) + 3)
        return time[0] + " " + ':'.join(time_arr)


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
    'attacker_embed': "Деф провинции?",
    'respawn_embed': "Респавн",
    'enemy_embed': "Противник",
    'fronts': fronts_ru,
    'fronts_inv': fronts_ru_inv,
    'pretenders': "Претенденты",
    'battles_embed': "Назначенный бой:"
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
    'attacker_embed': "Defence?",
    'respawn_embed': "Respawn",
    'enemy_embed': "Enemy",
    'fronts': fronts_eu,
    'fronts_inv': fronts_eu_inv,
    'pretenders': "Pretenders",
    'battles_embed': "Battle:"
}

region_map = {
    'ru': ru,
    'eu': eu
}
