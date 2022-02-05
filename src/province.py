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

    async def show_data(self):
        print(str(self.prime) + " " + str(self.map) + " " + str(self.map_2) + " " + str(self.channel) + " " + str(self.front))
        if is_none(self.prime) \
                or (is_none(self.map) and is_none(self.map_2)) \
                or (not is_none(self.map) and not is_none(self.map_2)) \
                or is_none(self.channel)\
                or is_none(self.front):
            return

        if self.map is None:
            self.map = self.map_2

        provinces = self.wg_api.get_provinces(int(self.prime), self.front)
        data = list(map(lambda x: x['data'], provinces))
        flattened = list(itertools.chain(*data))
        filtered = list(filter(lambda x: x['arena_id'] == self.map, flattened))

        if self.region == 'ru':
            print(str(len(filtered)))
            print(str(inv_maps[self.map]))
            await self.channel.send(
                "Найдено " + str(len(filtered)) + " провинций для карты - " + str(inv_maps[self.map]) +
                ", прайма - " + str(self.prime) + ":00/15, фронта - " + region_map[self.region]['fronts_inv'][self.front])
        else:
            print(str(len(filtered)))
            print(str(inv_maps[self.map]))
            await self.channel.send(
                "Found " + str(len(filtered)) + " provinces for the map - " + str(inv_maps[self.map]) +
                ", prime - " + str(self.prime) + ":00/15, Front - " + region_map[self.region]['fronts_inv'][self.front])
        for entry in filtered:
            embed, file = self.generate_embed(entry)
            await self.channel.send(file=file, embed=embed)

    def generate_embed(self, data):
        owner = data['owner_clan_id']
        if owner is None:
            owner = "This province has currently no owner."
        embed = Embed(
            color=discord.Color.gold(),
            title=data['province_name'],
            url=province_base_url + data['uri']
        )
        embed.add_field(
            name=region_map[self.region]['prime_embed'], value=str(data['prime_time']) + " UTC", inline=True)
        embed.add_field(
            name=region_map[self.region]['map_embed'], value=inv_maps[self.map], inline=True)
        embed.add_field(
            name=region_map[self.region]['server_embed'], value=data['server'], inline=True)
        embed.add_field(
            name=region_map[self.region]['min_bet_embed'], value=":coin: " + str(data['current_min_bet']), inline=True)
        embed.add_field(
            name=region_map[self.region]['last_won_bet_embed'], value=":coin: " + str(data['last_won_bet']), inline=True)
        embed.add_field(
            name=region_map[self.region]['front_embed'], value=region_map[self.region]['fronts_inv'][self.front], inline=True)
        embed.add_field(
            name=region_map[self.region]['owner_embed'], value=owner, inline=False)
        embed.add_field(
            name=region_map[self.region]['attackers_embed'], value="No attackers", inline=False)
        embed.add_field(
            name=region_map[self.region]['competitors_embed'], value="No competitors", inline=False)
        embed.set_image(
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

    async def select_prime(self, interaction):
        # print(interaction.data)
        self.disable_select("prime")
        self.prime = interaction.data['values'][0]
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_map(self, interaction):
        self.disable_select("map_2")
        self.disable_select("map")
        self.set_map(interaction.data['values'][0], 1)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_map_2(self, interaction):
        self.disable_select("map_2")
        self.disable_select("map")
        self.set_map(interaction.data['values'][0], 2)
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_front(self, interaction):
        self.disable_select("front")
        self.front = interaction.data['values'][0]
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    def disable_select(self, select):
        children = self.view.children
        for child in children:
            if child.custom_id == select:
                child.disabled = True

    def set_view(self, view):
        self.view = view


province_base_url = "https://eu.wargaming.net/globalmap"

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
    'Westfield': '23_westfield', #
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

prime_times_eu = [18, 19, 20, 21]
prime_times_ru = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 00]

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
    'prime_placeholder': "Выберите Прайм Тайм",
    'map_placeholder': "Выберите карту",
    'front_placeholder': "Выберите фронт",
    'prime_time_select': "Прайм - ",
    'map_select': "Карта - ",
    'front_select': "Фронт - ",
    'fronts': fronts_ru,
    'fronts_inv': fronts_ru_inv,
    'prime': prime_times_ru,
    'maps': maps_ru,
    'prime_embed': "Прайм Тайм",
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
    'prime_placeholder': "Select Prime Time",
    'map_placeholder': "Select Map",
    'front_placeholder': "Select Front Type",
    'prime_time_select': "Prime - ",
    'map_select': "Map - ",
    'front_select': "Front - ",
    'fronts': fronts_eu,
    'fronts_inv': fronts_eu_inv,
    'prime': prime_times_eu,
    'maps_1': maps_eu,
    'maps_2': maps_eu_2,
    'prime_embed': "Prime time",
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
    for prime in prime_times:
        selects.append(
            SelectOption(
                label=region_map[region]['prime_time_select'] + str(prime),
                value=str(prime)
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
