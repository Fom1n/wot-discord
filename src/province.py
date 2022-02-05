import itertools

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

        provinces = self.wg_api.get_provinces(int(self.prime), self.front, self.region)
        data = list(map(lambda x: x['data'], provinces))
        flattened = list(itertools.chain(*data))
        filtered = list(filter(lambda x: x['arena_id'] == self.map, flattened))

        if self.region == 'ru':
            await self.channel.send(
                "Найдено " + str(len(filtered)) + " провинций для карты - " + str(inv_maps[self.map]) +
                ", прайма (МСК) - " + str(region_map[self.region]['prime'][int(self.prime)]) + ":00/15, фронта - " +
                region_map[self.region]['fronts_inv'][self.front])
        else:
            await self.channel.send(
                "Found " + str(len(filtered)) + " provinces for the map - " + str(inv_maps[self.map]) +
                ", prime (CET) - " + str(region_map[self.region]['prime'][int(self.prime)]) + ":00/15, Front - " +
                region_map[self.region]['fronts_inv'][self.front])
        if self.server != "any":
            filtered = list(filter(lambda x: x['server'] == self.server, filtered))
            await self.channel.send(str(len(filtered)) + " провинций с выбранным сервером")
        for entry in filtered:
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
        owner = data['owner_clan_id']
        if owner is None:
            owner = "This province has currently no owner."
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
        embed.add_field(
            name=region_map[self.region]['owner_embed'], value=owner, inline=False)
        embed.add_field(
            name=region_map[self.region]['attackers_embed'], value="No attackers", inline=False)
        embed.add_field(
            name=region_map[self.region]['competitors_embed'], value="No competitors", inline=False)
        embed.set_thumbnail(
            url="attachment://map.png")

        file = discord.File(map_to_picture[inv_maps[self.map]], filename="map.png")
        return embed, file

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
    'Sand river': '28_desert',
    'Redshire': '34_reshire',
    'Steppes': '35_steppes',
    'Fisherman\'s Bay': '36_fishing_bay',
    'Mountain pass': '37_caucasus',
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
    'Mountain pass': '37_caucasus',
    'Overlord': '101_dday',
    'Pilsen': '114_czech',
    'Ruinberg': '08_ruinberg',
}

maps_eu_2 = {
    'Cliff': '18_cliff',
    'El hallouf': '29_el_hallouf',
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
    'Sand river': '28_desert',
    'Serene Coast': '47_canada_a',
    'Siegfried line': '14_sigfried_line',
    'Steppes': '35_steppes',
    'Tundra': '63_tundra',
    'Westfield': '23_westfield',  #
}

maps_all = {
    'Cliff': '18_cliff',
    'El hallouf': '29_el_hallouf',
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
    'Sand river': '28_desert',
    'Serene Coast': '47_canada_a',
    'Siegfried line': '14_sigfried_line',
    'Steppes': '35_steppes',
    'Tundra': '63_tundra',
    'Westfield': '23_westfield',
    'Abbey': '19_monastery',
    'Berlin': '105_germany',
    'Karelia': '01_karelia',
    'Mountain pass': '37_caucasus',
    'Overlord': '101_dday',
    'Pilsen': '114_czech',
    'Ruinberg': '08_ruinberg',
    'Lost City': '95_lost_city',
}

inv_maps = {v: k for k, v in maps_all.items()}

map_to_picture = {
    'Westfield': 'src/maps/23_westfeld.png',
    'Siegfried line': 'src/maps/14_siegfried_line.png',
    'Erlenberg': 'src/maps/13_erlenberg.png',
    'El hallouf': 'src/maps/29_el_hallouf.png',
    'Overlord': 'src/maps/101_dday.png',
    'Karelia': 'src/maps/01_karelia.png',
    'Malinovka': 'src/maps/02_malinovka.png',
    'Himmelsdorf': 'src/maps/04_himmelsdorf.png',
    'Prohorovka': 'src/maps/05_prohorovka.png',
    'Ensk': 'src/maps/06_ensk.png',
    'Lakeville': 'src/maps/07_lakeville.png',
    'Ruinberg': 'src/maps/08_ruinberg.png',
    'Hills': 'src/maps/10_hills.png',
    'Murovanka': 'src/maps/11_murovanka.png',
    'Cliff': 'src/maps/18_cliff.png',
    'Monastery': 'src/maps/19_monastery.png',
    'Sand river': 'src/maps/28_desert.png',
    'Redshire': 'src/maps/34_reshire.png',
    'Steppes': 'src/maps/35_steppes.png',
    'Fishing Bay': 'src/maps/36_fishing_bay.png',
    'Mountain pass': 'src/maps/37_caucasus.png',
    'Live Oaks': 'src/maps/44_north_america.png',
    'Highway': 'src/maps/45_north_america.png',
    'Serene Coast': 'src/maps/47_canada_a.png',
    'Pearl River': 'src/maps/60_asia_miao.png',
    'Lost City': 'src/maps/95_lost_city.png',
    'Pilsen': 'src/maps/114_czech.png',
    'Berlin': 'src/maps/105_germany.png'
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

ru = {
    'province_base_url': "https://ru.wargaming.net/globalmap",
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
    'competitors_embed': "Турнирные кланы"
}

eu = {
    'province_base_url': "https://eu.wargaming.net/globalmap",
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
    'competitors_embed': "Competitors clans"
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
