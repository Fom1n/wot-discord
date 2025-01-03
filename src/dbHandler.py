import sqlite3


class DbHandler:

    def updateChannel(self, guild_id, channel_id, channel_type, clan, region):
        try:
            exists = self.channelExists(guild_id, channel_id)
            if exists:
                self.updateExistingChannel(guild_id, channel_id, channel_type, clan, region)
            else:
                self.insertChannel(guild_id, channel_id, channel_type, clan, region)
            return True
        except sqlite3.Error as er:
            print(er)
            return True

    # Return True if transaction is successful
    # False if it failed (for any reason)
    def updateGuildClan(self, guild_id, clan_tag, clan_id):
        try:
            exists = self.guildClanExists(guild_id)
            if exists:
                self.updateExistingGuildClan(guild_id, clan_tag, clan_id)
            else:
                self.insertGuildClan(guild_id, clan_tag, clan_id)
            return True
        # For some reason it returns an error [near ".": syntax error] even if it successfully updated/inserted,
        # need to look into that
        except sqlite3.Error as er:
            print(er)
            return True

    def updateRegion(self, guild_id, region):
        try:
            exists = self.regionExists(guild_id)
            if exists:
                self.updateExistingRegion(guild_id, region)
            else:
                self.insertRegion(guild_id, region)
            return True
        except sqlite3.Error as er:
            print(er)
            return False

    def getRegion(self, guild_id):
        self.reconnect()
        cur = self.con.cursor()
        region = cur.execute('SELECT * FROM region WHERE guildId = ?', [guild_id]).fetchall()
        self.con.commit()
        self.con.close()
        if len(region) == 0:
            return None
        return region[0][1]

    def getChannelsAndClansInfo(self, channel_type):
        self.reconnect()
        cur = self.con.cursor()
        channels = cur.execute('SELECT * FROM channels WHERE type = ?', [channel_type]).fetchall()
        self.con.commit()
        self.con.close()
        return channels

    def getClanIds(self, guild_id):
        self.reconnect()
        cur = self.con.cursor()
        everything = cur.execute('SELECT * FROM clans WHERE guildId = ?;', [guild_id]).fetchall()[0]
        self.con.commit()
        self.con.close()
        return everything

    def regionExists(self, guild_id):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM region WHERE guildId = ?);', [guild_id]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    def updateExistingRegion(self, guild_id, region):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("UPDATE region "
                    "SET region = ?"
                    "WHERE guildId = ?", [region, guild_id])
        self.con.commit()
        self.con.close()

    def insertRegion(self, guild_id, region):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("INSERT INTO region VALUES (?, ?)", [guild_id, region])

        self.con.commit()
        self.con.close()

    def guildClanExists(self, guild_id):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM clans WHERE clans.guildId = ?);', [guild_id]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    def channelExists(self, guild_id, channel_id):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM channels '
                             'WHERE guildId = ? '
                             'AND channelId = ?);', [guild_id, channel_id]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    def updateExistingChannel(self, guild_id, channel_id, channel_type, clan, region):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("UPDATE channels "
                    "SET channelId = ?, "
                    "type = ?, "
                    "clan = ?, "
                    "region = ? "
                    "WHERE guildId = ? ", [channel_id, channel_type, clan, region, guild_id])
        self.con.commit()
        self.con.close()

    def insertChannel(self, guild_id, channel_id, channel_type, clan, region):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("INSERT INTO channels VALUES (?, ?, ?, ?, ?);", [guild_id, channel_id, channel_type, clan, region])

        self.con.commit()
        self.con.close()

    def updateExistingGuildClan(self, guild_id, clan_tag, clan_id):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("UPDATE clans "
                    "SET clan = ?, "
                    "clanId = ? "
                    "WHERE guildId = ?;", [clan_tag, clan_id, guild_id])
        self.con.commit()
        self.con.close()

    def insertGuildClan(self, guild_id, clan_tag, clan_id):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("INSERT INTO clans VALUES (?, ?, ?);", [guild_id, clan_tag, clan_id])

        self.con.commit()
        self.con.close()

    def delete_channel(self, channel_id, guild_id):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute('''DELETE FROM channels WHERE channelId = ? AND guildId = ?;''', [channel_id, guild_id])

        self.con.commit()
        self.con.close()

    def clan_name_and_id_exists(self, clan_tag, region):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM clan_to_id WHERE clan = ? AND region = ?);'
                             , [clan_tag, region]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    def get_clan_name_and_id(self, clan_tag, region):
        self.reconnect()

        cur = self.con.cursor()
        result = cur.execute('''SELECT * FROM clan_to_id WHERE clan = ? AND region = ?''', [clan_tag, region]).fetchall()

        self.con.commit()
        self.con.close()
        return result

    def insert_clan_name_and_id(self, clan_tag, clan_id, region):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute('''INSERT INTO clan_to_id VALUES (?, ?, ?)''', [clan_tag, clan_id, region])

        self.con.commit()
        self.con.close()

    # Idk, you need to close connection after each query to avoid confusion and info loss so there's that workaround
    def reconnect(self):
        self.con = sqlite3.connect('src/db/main.db')

    def __init__(self):
        self.con = sqlite3.connect('src/db/main.db')
        self.con.close()
