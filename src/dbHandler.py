import sqlite3


class DbHandler:

    def updateChannel(self, guild_id, channel_id, channel_type):
        try:
            exists = self.channelExists(guild_id, channel_type)
            if exists:
                self.updateExistingChannel(guild_id, channel_id, channel_type)
            else:
                self.insertChannel(guild_id, channel_id, channel_type)
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

    def getClanAndChannel(self, channel_type):
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

    def guildClanExists(self, guild_id):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM clans WHERE clans.guildId = ?);', [guild_id]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    def channelExists(self, guild_id, channel_type):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM channels '
                             'WHERE channels.guildId = ? '
                             'AND channels.type = ?);', [guild_id, channel_type]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    def updateExistingChannel(self, guild_id, channel_id, channel_type):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("UPDATE channels "
                    "SET channelId = ?"
                    "WHERE guildId = ? "
                    "AND type = ?;", [channel_id, guild_id, channel_type])
        self.con.commit()
        self.con.close()

    def insertChannel(self, guild_id, channel_id, channel_type):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("INSERT INTO channels VALUES (?, ?, ?);", [guild_id, channel_type, channel_id])

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

    # Idk, you need to close connection after each query to avoid confusion and info loss so there's that workaround
    def reconnect(self):
        self.con = sqlite3.connect('main.db')

    def __init__(self):
        self.con = sqlite3.connect('main.db')
        self.con.close()