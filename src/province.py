import itertools

import discord
from discord import SelectOption, InteractionResponded, Embed
from discord.ui import Select, View

from src.wgApi import wgApi


class Province:

    def __init__(self):
        self.view = None
        self.prime = None
        self.map = None
        self.channel = None
        self.front = None
        self.wg_api = wgApi()

    async def show_data(self):
        if self.prime is None or self.map is None or self.channel is None or self.front is None:
            return
        provinces = self.wg_api.get_provinces(int(self.prime), self.front)
        data = list(map(lambda x: x['data'], provinces))
        flattened = list(itertools.chain(*data))
        filtered = list(filter(lambda x: x['arena_id'] == self.map, flattened))
        print(filtered)
        await self.channel.send("Found " + str(len(filtered)) + " provinces for the map - " + str(inv_maps[self.map]) +
                                ", prime - " + str(self.prime) + ":00/15, Front - " + fronts_inv[self.front])
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
            url=province_base_url+data['uri']
        )
        embed.add_field(name="Prime time", value=str(data['prime_time']) + " UTC", inline=True)
        embed.add_field(name="Map", value=inv_maps[self.map], inline=True)
        embed.add_field(name="Server", value=data['server'], inline=True)
        embed.add_field(name="Current minimum bet", value=":coin: " + str(data['current_min_bet']), inline=True)
        embed.add_field(name="Last won bet", value=":coin: " + str(data['last_won_bet']), inline=True)
        embed.add_field(name="Front", value=fronts_inv[self.front], inline=True)
        embed.add_field(name="Owner (clickable)", value=owner, inline=False)
        embed.add_field(name="Attackers", value="No attackers", inline=False)
        embed.add_field(name="Competitors", value="No competitors", inline=False)
        embed.set_image(url="attachment://map.png")

        file = discord.File(map_to_picture[inv_maps[self.map]], filename="map.png")
        return embed, file


    async def select_prime(self, interaction):
        # print(interaction.data)
        self.disable_select("prime")
        self.prime = interaction.data['values'][0]
        self.channel = interaction.channel
        await interaction.response.edit_message(view=self.view)
        await self.show_data()

    async def select_map(self, interaction):
        self.disable_select("map")
        self.map = interaction.data['values'][0]
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

prime_times = [18, 19, 20, 21]
maps = {
    'Karelia': '01_karelia',
    'Malinovka': '02_malinovka',
    'Himmelsdorf': '04_himmelsdorf',
    'Prohorovka': '05_prohorovka',
    'Ensk': '06_ensk',
    'Lakeville': '07_lakeville',
    'Ruinberg': '08_ruinberg',
    'Hills': '10_hills',
    'Murovanka': '11_murovanka',
    # 'Erlenberg': '13_erlenberg',
    # 'Siegfried line': '14_sigfried_line',
    'Cliff': '18_cliff',
    'Monastery': '19_monastery',
    # 'Westfield': '23_westfield',
    'Sand river': '28_desert',
    # 'El hallouf': '29_el_hallouf',
    # 'Airfield': '31_airfield',
    # 'Fjord': '33_fjord',
    'Redshire': '34_reshire',
    'Steppes': '35_steppes',
    'Fishing Bay': '36_fishing_bay',
    'Mountain pass': '37_caucasus',
    # 'Mannerheim line': '38_mannerheim_line',
    'Live Oaks': '44_north_america',
    'Highway': '45_north_america',
    'Serene Coast': '47_canada_a',
    'Pearl River': '60_asia_miao',
    # 'Kharkiv': '83_kharkiv',
    # 'Minsk': '90_minsk',
    'Lost City': '95_lost_city',
    # 'Studzianki': '99_poland',
    # 'Berlin': '105_germany'
}

inv_maps = {v: k for k, v in maps.items()}

map_to_picture = {
    'Karelia': './maps/01_karelia.png',
    'Malinovka': './maps/02_malinovka.png',
    'Himmelsdorf': './maps/04_himmelsdorf.png',
    'Prohorovka': './maps/05_prohorovka.png',
    'Ensk': './maps/06_ensk.png',
    'Lakeville': './maps/07_lakeville.png',
    'Ruinberg': './maps/08_ruinberg.png',
    'Hills': './maps/10_hills.png',
    'Murovanka': './maps/11_murovanka.png',
    'Cliff': './maps/18_cliff.png',
    'Monastery': './maps/19_monastery.png',
    'Sand river': './maps/28_desert.png',
    'Redshire': './maps/34_reshire.png',
    'Steppes': './maps/35_steppes.png',
    'Fishing Bay': './maps/36_fishing_bay.png',
    'Mountain pass': './maps/37_caucasus.png',
    'Live Oaks': './maps/44_north_america.png',
    'Highway': './maps/45_north_america.png',
    'Serene Coast': './maps/47_canada_a.png',
    'Pearl River': './maps/60_asia_miao.png',
    'Lost City': './maps/95_lost_city.png',
}

fronts = {
    'Basic': "confrontation_eu_league1",
    'Advanced': "confrontation_eu_league2",
    'Elite': "confrontation_eu_league3"
}

fronts_inv = {v: k for k, v in fronts.items()}

def create_view():
    province = Province()
    select_prime = Select(
        custom_id="prime",
        placeholder="Select Prime Time",
        options=create_select_options_prime()
    )
    select_prime.callback = province.select_prime
    select_map = Select(
        custom_id="map",
        placeholder="Select Map",
        options=create_select_options_map()
    )
    select_map.callback = province.select_map
    select_front = Select(
        custom_id="front",
        placeholder="Select Front",
        options=create_select_options_front()
    )
    select_front.callback = province.select_front
    view = View()
    view.add_item(select_prime)
    view.add_item(select_map)
    view.add_item(select_front)
    province.set_view(view)
    return view

def create_select_options_front():
    selects = []
    for front in fronts:
        selects.append(
            SelectOption(
                label="Front - " + front,
                value=fronts[front]
            )
        )
    return selects



def create_select_options_prime():
    selects = []
    for prime in prime_times:
        selects.append(
            SelectOption(
                label="Prime time - " + str(prime),
                value=str(prime)
            )
        )
    return selects


def create_select_options_map():
    selects = []
    for key in maps:
        selects.append(
            SelectOption(
                label="Map - " + key,
                value=maps[key]
            )
        )
    return selects
