import requests
headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'worldoftanks.eu',
            'Pragma': 'no-cache',
            'Referer': 'https://worldoftanks.eu/eu/clanwars/rating/alley/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
            'X-CSRFToken': 'LZ9NIq0KJKZ0SFr5Ncu6pDX9aAgRDbBX',
            'X-Requested-With': 'XMLHttpRequest'
        }
result = requests.get("https://ru.wargaming.net/clans/wot/207365/api/globalmap/", headers={'Accept': 'application/json'})
print(result.json())
# arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# print(arr[:3])
# print(arr[3:6])
# print(arr[6:10])