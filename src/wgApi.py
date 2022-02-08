import requests
import os


class wgApi:

    def get_clan_id(self, clan, region):
        params = {
            'application_id': os.getenv('API_KEY'),
            'game': 'wot',
            'search': clan,
            'limit': 1
        }
        result = requests.get(url=self.region_map[region]['url_clans'], params=params)
        return result.json()

    def get_clan_info(self, clan_id, region):
        result = requests.get(url=self.region_map[region]['clan_info_base'] + str(clan_id) + "/api/claninfo/")
        return result.json()

    def get_clan_sh_info(self, clan_id, region):
        params = {
            'application_id': os.getenv('API_KEY'),
            'clan_id': clan_id
        }
        result = requests.get(url=self.region_map[region]['sh_clan_info'], params=params)
        return result.json()

    def get_clan_details(self, clan_id, region):
        params = {
            'application_id': os.getenv('API_KEY'),
            'clan_id': clan_id
        }
        result = requests.get(url=self.region_map[region]['clan_details'], params=params)
        return result.json()

    def get_player_fame_details(self, clan, region):
        params = {
            'event_id': 'confrontation',
            'front_id': 'confrontation_bg',
            'page': 0,
            'page_size': 25,
            'user': "",
            'clan': clan
        }
        result = requests.get(self.region_map[region]['fame_points_base'],
                              headers=self.region_map[region]['fame_header'], params=params)
        return result.json()

    def get_provinces(self, prime_time, front, region, arena_id):
        i = 1
        params = {
            'application_id': os.getenv('API_KEY'),
            'front_id': front,
            'prime_hour': int(prime_time),
            'arena_id': arena_id,
            'order_by': "prime_hour",
            'fields': "arena_id, arena_name, attackers, competitors, prime_time, current_min_bet,"
                      " last_won_bet, owner_clan_id, province_name, server, uri, province_id",
            'page_no': i
        }
        results = []
        result = requests.get(url=self.region_map[region]['provinces'], params=params).json()
        while result['meta']['count'] == 100:
            results.append(result)
            i = i + 1
            params['page_no'] = i
            result = requests.get(url=self.region_map[region]['provinces'], params=params).json()
        results.append(result)
        return results

    def get_clan_global_map_info(self, clan_id, region):
        result = requests.get(url=self.region_map[region]['clan_info_base'] + str(clan_id) + "/api/globalmap/")
        result = result.json()['globalmap']
        return result

    def get_province_info(self, province_id, region):
        params = {
            'alias': province_id
        }
        result = requests.get(url=self.region_map[region]['province_info_base'], params=params)
        return result.json()

    def get_global_map_battles_info(self, clan_id, region):
        url = self.region_map[region]['battles_base'] + str(clan_id) + "/battles"
        result = requests.get(url=url)
        return result.json()

    def __init__(self):
        self.ru = {
            'url_clans': "https://api.worldoftanks.ru/wgn/clans/list/",
            'url_clan_info': "https://api.worldoftanks.ru/wot/stronghold/claninfo/",
            'sh_clan_info': "https://api.worldoftanks.ru/wot/stronghold/claninfo/",
            'clan_details': "https://api.worldoftanks.ru/wot/clans/info/",
            'fame_points_base': "https://worldoftanks.ru/ru/clanwars/rating/alley/users/search/by/clan/",
            'provinces': "https://api.worldoftanks.ru/wot/globalmap/provinces/",
            'clan_info_base': "https://ru.wargaming.net/clans/wot/",
            'province_info_base': "https://ru.wargaming.net/globalmap/game_api/province_info/",
            'fame_header': fame_ru,
            'battles_base': "https://ru.wargaming.net/globalmap/game_api/clan/"
        }
        self.eu = {
            'url_clans': "https://api.worldoftanks.eu/wgn/clans/list/",
            'url_clan_info': "https://api.worldoftanks.eu/wot/stronghold/claninfo/",
            'sh_clan_info': "https://api.worldoftanks.eu/wot/stronghold/claninfo/",
            'clan_details': "https://api.worldoftanks.eu/wot/clans/info/",
            'fame_points_base': "https://worldoftanks.eu/en/clanwars/rating/alley/users/search/by/clan/",
            'provinces': "https://api.worldoftanks.eu/wot/globalmap/provinces/",
            'clan_info_base': "https://eu.wargaming.net/clans/wot/",
            'province_info_base': "https://eu.wargaming.net/globalmap/game_api/province_info/",
            'fame_header': fame_eu,
            'battles_base': "https://eu.wargaming.net/globalmap/game_api/clan/"
        }
        self.region_map = {
            'ru': self.ru,
            'eu': self.eu
        }

fame_ru = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'worldoftanks.ru',
            'Pragma': 'no-cache',
            'Referer': 'https://worldoftanks.ru/ru/clanwars/rating/alley/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
            'X-CSRFToken': 'LZ9NIq0KJKZ0SFr5Ncu6pDX9aAgRDbBX',
            'X-Requested-With': 'XMLHttpRequest'
        }

fame_eu = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'worldoftanks.eu',
            'Pragma': 'no-cache',
            'Referer': 'https://worldoftanks.eu/en/clanwars/rating/alley/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
            'X-CSRFToken': 'LZ9NIq0KJKZ0SFr5Ncu6pDX9aAgRDbBX',
            'X-Requested-With': 'XMLHttpRequest'
        }