import requests
import os


class wgApi:

    def get_clan_id(self, clan):
        params = {
            'application_id': os.getenv('API_KEY'),
            'game': 'wot',
            'search': clan,
            'limit': 1
        }
        result = requests.get(url=self.URL_CLANS, params=params)
        return result.json()

    def get_clan_info(self, clan_id):
        params = {
            'application_id': os.getenv('API_KEY'),
            'clan_id': clan_id
        }
        result = requests.get(url=self.URL_CLAN_INFO, params=params)
        return result.json()

    def get_clan_sh_info(self, clan_id):
        params = {
            'application_id': os.getenv('API_KEY'),
            'clan_id': clan_id
        }
        result = requests.get(url=self.SH_CLAN_INFO, params=params)
        return result.json()

    def get_clan_details(self, clan_id):
        params = {
            'application_id': os.getenv('API_KEY'),
            'clan_id': clan_id
        }
        result = requests.get(url=self.CLAN_DETAILS, params=params)
        return result.json()

    def get_player_fame_details(self, account_id):
        params = {
            'application_id': os.getenv('API_KEY'),
            'account_id': str(account_id),
            'event_id': 'thunderstorm',
            'front_id': 'thunderstorm_bg',
            'fields': 'events.award_level, events.fame_points, events.account_id'
        }
        result = requests.get(url=self.PLAYER_FAME_INFO, params=params)
        return result.json()

    def get_provinces(self, prime_time, front):
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
        result = requests.get(url=self.PROVINCES, params=params).json()
        print(result)
        while result['meta']['count'] == 100:
            print(result)
            results.append(result)
            i = i + 1
            params['page_no'] = i
            result = requests.get(url=self.PROVINCES, params=params).json()
        print(result)
        results.append(result)
        return results

    def __init__(self):
        self.URL_CLANS = "https://api.worldoftanks.eu/wgn/clans/list/"
        self.URL_CLAN_INFO = "https://api.worldoftanks.eu/wot/stronghold/claninfo/"
        self.SH_CLAN_INFO = "https://api.worldoftanks.eu/wot/stronghold/claninfo/"
        self.CLAN_DETAILS = "https://api.worldoftanks.eu/wot/clans/info/"
        self.PLAYER_FAME_INFO = "https://api.worldoftanks.eu/wot/globalmap/eventaccountinfo/"
        self.PROVINCES = "https://api.worldoftanks.eu/wot/globalmap/provinces/"
