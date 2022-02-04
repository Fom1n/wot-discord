
class clanUtils:

    def calculate_sh_10_winrate(self, sh_info, clan_id):
        ten_played = sh_info['data'][str(clan_id)]['battles_for_strongholds_statistics']['total_10_in_28d']
        print(sh_info)
        ten_won = sh_info['data'][str(clan_id)]['battles_for_strongholds_statistics']['win_10_in_28d']
        if ten_played == 0:
            return str(0) + "%"
        format_wr = "{:.3f}".format(ten_won/ten_played)
        format_wr = float(format_wr) * 100
        return str(format_wr) + "%"

    def get_player_ids(self, info, clan_id):
        members = info['data'][str(clan_id)]['members']
        account_ids = map(lambda x: x['account_id'], members)
        return list(account_ids)

    def get_player_names(self, info, clan_id):
        members = info['data'][str(clan_id)]['members']
        player_names = map(lambda x: x['account_name'], members)
        return list(player_names)

    def __init__(self):
        pass
