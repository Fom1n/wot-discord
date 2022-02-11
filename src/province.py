import itertools
import math

import discord
from discord import SelectOption, InteractionResponded, Embed
from discord.ui import Select, View

from src.wgApi import wgApi


def is_none(val):
    return val is None


class Province:

    def __init__(self, region):
        self.view = None
        self.prime = None
        self.map = None
        self.map_2 = None
        self.channel = None
        self.front = None
        self.wg_api = wgApi()
        self.region = region
        if region == 'eu':
            self.server = 'any'
        else:
            self.server = None

    async def show_data(self):
        print(str(self.prime) + " " + str(self.map) + " " + str(self.map_2) + " " + str(self.channel) + " " + str(
            self.front))
        if is_none(self.prime) \
                or (is_none(self.map) and is_none(self.map_2)) \
                or (not is_none(self.map) and not is_none(self.map_2)) \
                or is_none(self.channel) \
                or is_none(self.front) \
                or is_none(self.server):
            return

        if self.map is None:
            self.map = self.map_2
        try:
            provinces = self.wg_api.get_provinces(int(self.prime), self.front, self.region, self.map)
        except KeyError as e:
            await self.channel.send("WG API ERROR (retry)")
            return
        data = list(map(lambda x: x['data'], provinces))
        flattened = list(itertools.chain(*data))
        # filtered = list(filter(lambda x: x['arena_id'] == self.map, flattened))
        if self.region == 'ru':
            await self.channel.send(
                "Найдено " + str(len(flattened)) + " провинций для карты - " + str(inv_maps[self.map]) +
                ", прайма (МСК) - " + str(region_map[self.region]['prime'][int(self.prime)]) + ":00/15, фронта - " +
                region_map[self.region]['fronts_inv'][self.front])
        else:
            await self.channel.send(
                "Found " + str(len(flattened)) + " provinces for the map - " + str(inv_maps[self.map]) +
                ", prime (CET) - " + str(region_map[self.region]['prime'][int(self.prime)]) + ":00/15, Front - " +
                region_map[self.region]['fronts_inv'][self.front])
        if self.server != "any":
            flattened = list(filter(lambda x: x['server'] == self.server, flattened))
            await self.channel.send(str(len(flattened)) + " провинций с выбранным сервером")
        for entry in flattened:
            # entry['competitors'] = [
            #     500066861,
            #     500000338,
            #     500197237,
            #     500072861,
            #     500071584,
            #     500161727,
            #     500205311,
            #     500010805,
            #     500161393,
            #     500008017,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861,
            #     500066861
            # ]
            # entry['owner_clan_id'] = 500205311
            embed, file = self.generate_embed(entry)
            await self.channel.send(file=file, embed=embed)

    def generate_embed(self, data):
        prime_time = str(data['prime_time'])
        if self.region == 'eu':
            prime_time = str(int(prime_time.split(':')[0]) + 1) + ":" + prime_time.split(':')[1]
        else:
            timezone_hour = int(prime_time.split(':')[0]) + 3
            if timezone_hour == 24:
                timezone_hour = 00
            prime_time = str(timezone_hour) + ":" + prime_time.split(':')[1]
        embed = Embed(
            color=discord.Color.gold(),
            title=data['province_name'],
            url=region_map[self.region]['province_base_url'] + data['uri']
        )
        embed.add_field(
            name=region_map[self.region]['prime_embed'], value=prime_time, inline=True)
        embed.add_field(
            name=region_map[self.region]['map_embed'], value=inv_maps[self.map], inline=True)
        embed.add_field(
            name=region_map[self.region]['server_embed'], value=data['server'], inline=True)
        embed.add_field(
            name=region_map[self.region]['min_bet_embed'], value=":coin: " + str(data['current_min_bet']), inline=True)
        embed.add_field(
            name=region_map[self.region]['last_won_bet_embed'], value=":coin: " + str(data['last_won_bet']),
            inline=True)
        embed.add_field(
            name=region_map[self.region]['front_embed'], value=region_map[self.region]['fronts_inv'][self.front],
            inline=True)
        # embed.add_field(
        #     name=region_map[self.region]['owner_embed'], value=owner, inline=False)
        owner = data['owner_clan_id']
        competitors = data['competitors']
        attackers = data['attackers']
        province_id = data['province_id']
        self.handle_owner(owner, embed)
        self.handle_clans(embed, attackers, 'attackers_embed')
        self.handle_clans(embed, competitors, 'competitors_embed')
        self.handle_bonuses(embed, province_id)

        embed.set_thumbnail(
            url="attachment://map.png")
        file = discord.File(map_to_picture[inv_maps[self.map]], filename="map.png")
        return embed, file

    def handle_owner(self, clan_id, embed):
        if is_none(clan_id):
            embed.add_field(
                name=region_map[self.region]['owner_embed'],
                value="---------"
            )
            return
        string = ""
        clan_info_gm = self.wg_api.get_clan_global_map_info(str(clan_id), self.region)
        clan_info_general = self.wg_api.get_clan_info(clan_id, self.region)
        global_map_elo = clan_info_gm['gm_elo_rating_10']
        clan_tag = clan_info_general['clanview']['clan']['tag']
        string = string + "[[" + clan_tag + "]](" + region_map[self.region]['clan_base_url'] + str(clan_id) + \
                 ") - Elo = " + str(global_map_elo) + "\n"
        embed.add_field(
            name=region_map[self.region]['owner_embed'],
            value=string
        )

    def handle_bonuses(self, embed, province_id):
        try:
            province_info = self.wg_api.get_province_info(province_id, self.region)['province']
        except KeyError:
            # await self.channel.send("WG PROVINCE ERROR (RETRY)")
            return
        bonuses = province_info['bonuses']
        string = ""
        for bonus in bonuses:
            bonus_type = bonus['bonus_type']
            bonus_value = str(bonus['bonus_value'])
            if str(bonus_type).startswith("FREE"):
                string = string + region_map[self.region]['bonus'][bonus_type] + " - " + bonus_value + "\n"
            else:
                string = string + region_map[self.region]['bonus'][bonus_type] + " - " + bonus_value + "%\n"
        embed.add_field(name=region_map[self.region]['bonus_embed'], value=string)

    def handle_clans(self, embed, clans, clan_type):
        if len(clans) == 0:
            embed.add_field(
                name=region_map[self.region][clan_type],
                value="---------", inline=False)
        elif len(clans) <= 10:
            embed.add_field(
                name=region_map[self.region][clan_type] + ", " + region_map[self.region]['length'] + str(len(clans)),
                value=self.generate_clans_string(clans), inline=False)
        elif len(clans) > 10:
            three = math.floor(len(clans)/3)
            embed.add_field(
                name=region_map[self.region][clan_type] + ", " + region_map[self.region]['length'] + str(len(clans)),
                value=self.generate_clans_string(clans[:three]), inline=False)
            embed.add_field(
                name=region_map[self.region][clan_type] + ", " + region_map[self.region]['length'] + str(len(clans)),
                value=self.generate_clans_string(clans[three:three*2]), inline=False)
            embed.add_field(
                name=region_map[self.region][clan_type] + ", " + region_map[self.region]['length'] + str(len(clans)),
                value=self.generate_clans_string(clans[three*2:]), inline=False)

    def generate_clans_string(self, clans):
        string = ""
        for clan in clans:
            clan_info_gm = self.wg_api.get_clan_global_map_info(str(clan), self.region)
            clan_info_general = self.wg_api.get_clan_info(clan, self.region)
            global_map_elo = clan_info_gm['gm_elo_rating_10']
            clan_tag = clan_info_general['clanview']['clan']['tag']
            string = string + "[[" + clan_tag + "]](" + region_map[self.region]['clan_base_url'] + str(clan) + \
                     ") - Elo = " + str(global_map_elo) + "\n"
        return string

    def set_map(self, select_map, map_nr):
        if select_map == 'none':
            if map_nr == 2:
                self.map_2 = None
            else:
                self.map = None
        else:
            if map_nr == 2:
                self.map_2 = select_map
            else:
                self.map = select_map

    async def select_server(self, interaction):
        self.server = interaction.data['values'][0]
        placeholder = "Выбранный сервер - " + self.server
        self.disable_select("server", placeholder)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_prime(self, interaction):
        self.prime = interaction.data['values'][0]
        placeholder = "Selected prime - " + str(region_map[self.region]['prime'][int(self.prime)]) + ":00/15"
        self.disable_select("prime", placeholder)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_map(self, interaction):
        self.set_map(interaction.data['values'][0], 1)
        placeholder = "Selected map - " + inv_maps[self.map]
        self.disable_select("map_2", placeholder)
        self.disable_select("map", placeholder)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_map_2(self, interaction):
        self.set_map(interaction.data['values'][0], 2)
        placeholder = "Selected map - " + inv_maps[self.map_2]
        self.disable_select("map_2", placeholder)
        self.disable_select("map", placeholder)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_front(self, interaction):
        self.front = interaction.data['values'][0]
        placeholder = "Selected Prime - " + region_map[self.region]['fronts_inv'][self.front]
        self.disable_select("front", placeholder)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    def is_child_active(self, select):
        children = self.view.children
        for child in children:
            if child.custom_id == select:
                return child.disabled

    def disable_select(self, select, val):
        children = self.view.children
        for child in children:
            if child.custom_id == select:
                child.disabled = True
                child.placeholder = val

    def set_view(self, view):
        self.view = view


maps_ru = {
    'Karelia': '01_karelia',
    'Malinovka': '02_malinovka',
    'Himmelsdorf': '04_himmelsdorf',
    'Prokhorovka': '05_prohorovka',
    'Ensk': '06_ensk',
    'Lakeville': '07_lakeville',
    'Ruinberg': '08_ruinberg',
    'Mines': '10_hills',
    'Murovanka': '11_murovanka',
    'Cliff': '18_cliff',
    'Abbey': '19_monastery',
    'Sand River': '28_desert',
    'Redshire': '34_reshire',
    'Steppes': '35_steppes',
    'Fisherman\'s Bay': '36_fishing_bay',
    'Mountain Pass': '37_caucasus',
    'Live Oaks': '44_north_america',
    'Highway': '45_north_america',
    'Serene Coast': '47_canada_a',
    'Pearl River': '60_asia_miao',
    'Lost City': '95_lost_city',
}

maps_eu = {
    'Abbey': '19_monastery',
    'Berlin': '105_germany',
    'Karelia': '01_karelia',
    'Mountain Pass': '37_caucasus',
    'Overlord': '101_dday',
    'Pilsen': '114_czech',
    'Ruinberg': '08_ruinberg',
}

maps_eu_2 = {
    'Cliff': '18_cliff',
    'El Halluf': '29_el_hallouf',
    'Ensk': '06_ensk',
    'Erlenberg': '13_erlenberg',
    'Fisherman\'s Bay': '36_fishing_bay',
    'Highway': '45_north_america',
    'Himmelsdorf': '04_himmelsdorf',
    'Lakeville': '07_lakeville',
    'Live Oaks': '44_north_america',
    'Malinovka': '02_malinovka',
    'Mines': '10_hills',
    'Murovanka': '11_murovanka',
    'Pearl River': '60_asia_miao',
    'Prokhorovka': '05_prohorovka',
    'Redshire': '34_reshire',
    'Sand River': '28_desert',
    'Serene Coast': '47_canada_a',
    'Siegfried line': '14_sigfried_line',
    'Steppes': '35_steppes',
    'Tundra': '63_tundra',
    'Westfield': '23_westfield',  #
    'Paris': '112_eiffel_tower_ctf'
}

maps_all = {
    'Cliff': '18_cliff',
    'El Halluf': '29_el_hallouf',
    'Ensk': '06_ensk',
    'Erlenberg': '13_erlenberg',
    'Fisherman\'s Bay': '36_fishing_bay',
    'Highway': '45_north_america',
    'Хайвей': '45_north_america',
    'Himmelsdorf': '04_himmelsdorf',
    'Lakeville': '07_lakeville',
    'Live Oaks': '44_north_america',
    'Лайв Окс': '44_north_america',
    'Malinovka': '02_malinovka',
    'Mines': '10_hills',
    'Murovanka': '11_murovanka',
    'Pearl River': '60_asia_miao',
    'Жемчужная река': '60_asia_miao',
    'Prokhorovka': '05_prohorovka',
    'Redshire': '34_reshire',
    'Sand River': '28_desert',
    'Serene Coast': '47_canada_a',
    'Тихий берег': '47_canada_a',
    'Siegfried line': '14_sigfried_line',
    'Steppes': '35_steppes',
    'Tundra': '63_tundra',
    'Westfield': '23_westfield',
    'Abbey': '19_monastery',
    'Berlin': '105_germany',
    'Karelia': '01_karelia',
    'Mountain Pass': '37_caucasus',
    'Перевал': '37_caucasus',
    'Overlord': '101_dday',
    'Pilsen': '114_czech',
    'Ruinberg': '08_ruinberg',
    'Lost City': '95_lost_city',
    'Paris': '112_eiffel_tower_ctf'
}

inv_maps = {v: k for k, v in maps_all.items()}

map_to_picture = {
    'Westfield': 'src/maps/23_westfeld.png',
    'Вестфилд': 'src/maps/23_westfeld.png',
    'Siegfried Line': 'src/maps/14_siegfried_line.png',
    'Erlenberg': 'src/maps/13_erlenberg.png',
    'El Halluf': 'src/maps/29_el_hallouf.png',
    'Overlord': 'src/maps/101_dday.png',
    'Karelia': 'src/maps/01_karelia.png',
    'Карелия': 'src/maps/01_karelia.png',
    'Malinovka': 'src/maps/02_malinovka.png',
    'Малиновка': 'src/maps/02_malinovka.png',
    'Himmelsdorf': 'src/maps/04_himmelsdorf.png',
    'Химмельсдорф': 'src/maps/04_himmelsdorf.png',
    'Prokhorovka': 'src/maps/05_prohorovka.png',
    'Прохоровка': 'src/maps/05_prohorovka.png',
    'Ensk': 'src/maps/06_ensk.png',
    'Энск': 'src/maps/06_ensk.png',
    'Lakeville': 'src/maps/07_lakeville.png',
    'Ласвилль': 'src/maps/07_lakeville.png',
    'Ruinberg': 'src/maps/08_ruinberg.png',
    'Руинберг': 'src/maps/08_ruinberg.png',
    'Mines': 'src/maps/10_hills.png',
    'Рудники': 'src/maps/10_hills.png',
    'Murovanka': 'src/maps/11_murovanka.png',
    'Мурованка': 'src/maps/11_murovanka.png',
    'Cliff': 'src/maps/18_cliff.png',
    'Утёс': 'src/maps/18_cliff.png',
    'Abbey': 'src/maps/19_monastery.png',
    'Монастырь': 'src/maps/19_monastery.png',
    'Sand River': 'src/maps/28_desert.png',
    'Песчаная река': 'src/maps/28_desert.png',
    'Redshire': 'src/maps/34_reshire.png',
    'Редшир': 'src/maps/34_reshire.png',
    'Steppes': 'src/maps/35_steppes.png',
    'Степи': 'src/maps/35_steppes.png',
    'Fisherman\'s Bay': 'src/maps/36_fishing_bay.png',
    'Рыбацкая бухта': 'src/maps/36_fishing_bay.png',
    'Mountain Pass': 'src/maps/37_caucasus.png',
    'Перевал': 'src/maps/37_caucasus.png',
    'Live Oaks': 'src/maps/44_north_america.png',
    'Highway': 'src/maps/45_north_america.png',
    'Serene Coast': 'src/maps/47_canada_a.png',
    'Pearl River': 'src/maps/60_asia_miao.png',
    'Lost City': 'src/maps/95_lost_city.png',
    'Затерянный город': 'src/maps/95_lost_city.png',
    'Pilsen': 'src/maps/114_czech.png',
    'Berlin': 'src/maps/105_germany.png',
    'Paris': 'src/maps/112_eiffel_tower_ctf.png',
    'Safe Haven': 'src/maps/127_japort.png',
    'Studzianki': 'src/maps/99_poland.png'
}

prime_times_eu = {
    18: 19,
    19: 20,
    20: 21,
    21: 22
}
prime_times_ru = {
    11: 14,
    12: 15,
    13: 16,
    14: 17,
    15: 18,
    16: 19,
    17: 20,
    18: 21,
    20: 22,
    21: 23
}

prime_times_eu_inv = {v: k for k, v in prime_times_eu.items()}
prime_times_ru_inv = {v: k for k, v in prime_times_ru.items()}

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

servers_ru = {
    'Любой': 'any',
    'RU2': 'RU2',
    'RU4': 'RU4',
    'RU6': 'RU6',
    'RU8': 'RU8'
}

bonus_map_ru = {
    'CFP_BATTLES': "Клановые очки славы в боях",
    'CFP_PROVINCE': "Клановые очки славы с провинций",
    'CFP_PRIZE': "Бонус за количество захваченных провинций",
    'FREE_APPLIC_L2': "Заявки на высадку на Продвинутый Фронт, в день",
    'FREE_APPLIC_L3': "Заявки на высадку на Элитный Фронт, в день"
}

bonus_map_eu = {
    'CFP_BATTLES': "Clan Fame Points in battles",
    'CFP_PROVINCE': "Clan Fame Pooints from provinces",
    'CFP_PRIZE': "Bonus for the number of captured provinces",
    'FREE_APPLIC_L2': "Applications for landing in the Advanced Front, per day",
    'FREE_APPLIC_L3': "Applications for landing in the Elite Front, per day"
}

ru = {
    'province_base_url': "https://ru.wargaming.net/globalmap",
    'clan_base_url': "https://ru.wargaming.net/clans/wot",
    'prime_placeholder': "Выберите Прайм Тайм",
    'map_placeholder': "Выберите карту",
    'front_placeholder': "Выберите фронт",
    'prime_time_select': "Прайм (МСК) - ",
    'map_select': "Карта - ",
    'front_select': "Фронт - ",
    'fronts': fronts_ru,
    'fronts_inv': fronts_ru_inv,
    'prime': prime_times_ru,
    'prime_inv': prime_times_ru_inv,
    'maps': maps_ru,
    'prime_embed': "Прайм Тайм (МСК)",
    'map_embed': "Карта",
    'server_embed': "Сервер",
    'min_bet_embed': "Минимальная ставка",
    'last_won_bet_embed': "Последняя выигрышная ставка",
    'front_embed': "Фронт",
    'owner_embed': "Владелец",
    'attackers_embed': "Атакующие кланы",
    'competitors_embed': "Турнирные кланы",
    'bonus': bonus_map_ru,
    'bonus_embed': "Бонусы провинции",
    'length': "Количество кланов - "
}

eu = {
    'province_base_url': "https://eu.wargaming.net/globalmap",
    'clan_base_url': "https://eu.wargaming.net/clans/wot/",
    'prime_placeholder': "Select Prime Time",
    'map_placeholder': "Select Map",
    'front_placeholder': "Select Front Type",
    'prime_time_select': "Prime (CET) - ",
    'map_select': "Map - ",
    'front_select': "Front - ",
    'fronts': fronts_eu,
    'fronts_inv': fronts_eu_inv,
    'prime': prime_times_eu,
    'prime_inv': prime_times_eu_inv,
    'maps_1': maps_eu,
    'maps_2': maps_eu_2,
    'prime_embed': "Prime time (CET)",
    'map_embed': "Map",
    'server_embed': "Server",
    'min_bet_embed': "Minimum bet",
    'last_won_bet_embed': "Last won bet",
    'front_embed': "Front",
    'owner_embed': "Province owner",
    'attackers_embed': "Attackers clans",
    'competitors_embed': "Competitors clans",
    'bonus': bonus_map_eu,
    'bonus_embed': "Province bonuses",
    'length': "Number of clans - "
}

region_map = {
    'ru': ru,
    'eu': eu
}


def create_view(region):
    view = View()
    province = Province(region)
    select_prime = Select(
        custom_id="prime",
        placeholder=region_map[region]['prime_placeholder'],
        options=create_select_options_prime(region)
    )
    select_prime.callback = province.select_prime
    select_front = Select(
        custom_id="front",
        placeholder=region_map[region]['front_placeholder'],
        options=create_select_options_front(region)
    )
    select_front.callback = province.select_front
    if region == 'ru':
        select_map = Select(
            custom_id="map",
            placeholder=region_map[region]['map_placeholder'],
            options=create_select_options_map(region, maps_ru)
        )
        select_map.callback = province.select_map
        view.add_item(select_map)
        select_server = Select(
            custom_id="server",
            placeholder="Выберите сервер",
            options=create_server_select_ru()
        )
        select_server.callback = province.select_server
        view.add_item(select_server)
    else:
        select_map_one = Select(
            custom_id="map",
            placeholder=region_map[region]['map_placeholder'],
            options=create_select_options_map(region, maps_eu)
        )
        select_map_one.callback = province.select_map
        select_map_two = Select(
            custom_id="map_2",
            placeholder=region_map[region]['map_placeholder'],
            options=create_select_options_map(region, maps_eu_2)
        )
        select_map_two.callback = province.select_map_2
        view.add_item(select_map_one)
        view.add_item(select_map_two)
    view.add_item(select_prime)
    view.add_item(select_front)
    province.set_view(view)
    return view


def create_select_options_front(region):
    selects = []
    fronts = region_map[region]['fronts']
    for front in fronts:
        selects.append(
            SelectOption(
                label=region_map[region]['front_select'] + front,
                value=fronts[front]
            )
        )
    return selects


def create_select_options_prime(region):
    selects = []
    prime_times = region_map[region]['prime']
    for key in prime_times:
        selects.append(
            SelectOption(
                label=region_map[region]['prime_time_select'] + str(prime_times[key]),
                value=str(key)
            )
        )
    return selects


def create_select_options_map(region, maps):
    selects = []
    for key in maps:
        selects.append(
            SelectOption(
                label=region_map[region]['map_select'] + key,
                value=maps[key]
            )
        )
    return selects


def create_server_select_ru():
    selects = []
    for key in servers_ru:
        selects.append(
            SelectOption(
                label="Сервер - " + key,
                value=servers_ru[key]
            )
        )
    return selects
