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
        params = {
            'application_id': os.getenv('API_KEY'),
            'clan_id': clan_id
        }
        result = requests.get(url=self.region_map[region]['url_clan_info'], params=params)
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

    def get_player_fame_details(self, account_id, region):
        params = {
            'application_id': os.getenv('API_KEY'),
            'account_id': str(account_id),
            'event_id': 'thunderstorm',
            'front_id': 'thunderstorm_bg',
            'fields': 'events.award_level, events.fame_points, events.account_id'
        }
        result = requests.get(url=self.region_map[region]['player_fame_info'], params=params)
        return result.json()

    def get_provinces(self, prime_time, front, region):
        i = 1
        params = {
            'application_id': os.getenv('API_KEY'),
            'front_id': front,
            'prime_hour': int(prime_time),
            'fields': "arena_id, arena_name, attackers, competitors, prime_time, current_min_bet,"
                      " last_won_bet, owner_clan_id, province_name, server, uri",
            'page_no': i
        }
        results = []
        result = requests.get(url=self.region_map[region]['provinces'], params=params).json()
        print(result['meta'])
        while result['meta']['count'] == 100:
            print(result)
            results.append(result)
            i = i + 1
            params['page_no'] = i
            result = requests.get(url=self.region_map[region]['provinces'], params=params).json()
        print(result['meta'])
        results.append(result)
        return results

    def __init__(self):
        self.ru = {
            'url_clans': "https://api.worldoftanks.ru/wgn/clans/list/",
            'url_clan_info': "https://api.worldoftanks.ru/wot/stronghold/claninfo/",
            'sh_clan_info': "https://api.worldoftanks.ru/wot/stronghold/claninfo/",
            'clan_details': "https://api.worldoftanks.ru/wot/clans/info/",
            'player_fame_info': "https://api.worldoftanks.ru/wot/globalmap/eventaccountinfo/",
            'provinces': "https://api.worldoftanks.ru/wot/globalmap/provinces/"
        }
        self.eu = {
            'url_clans': "https://api.worldoftanks.eu/wgn/clans/list/",
            'url_clan_info': "https://api.worldoftanks.eu/wot/stronghold/claninfo/",
            'sh_clan_info': "https://api.worldoftanks.eu/wot/stronghold/claninfo/",
            'clan_details': "https://api.worldoftanks.eu/wot/clans/info/",
            'player_fame_info': "https://api.worldoftanks.eu/wot/globalmap/eventaccountinfo/",
            'provinces': "https://api.worldoftanks.eu/wot/globalmap/provinces/"
        }
        self.region_map = {
            'ru': self.ru,
            'eu': self.eu
        }
