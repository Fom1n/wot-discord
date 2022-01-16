import sqlite3


class DbHandler:

    def guildClanExists(self, guild_id):
        self.reconnect()

        cur = self.con.cursor()
        exists = cur.execute('SELECT EXISTS(SELECT 1 FROM clans WHERE clans.guildId = ?);', [guild_id]).fetchall()[0][0]
        self.con.close()
        if exists == 1:
            return True
        else:
            return False

    # Return True if transaction is successful
    # False if it failed (for any reason)
    def updateGuildClan(self, guild_id, clan_tag):
        try:
            exists = self.guildClanExists(guild_id)
            if exists:
                self.updateExistingGuildClan(guild_id, clan_tag)
            else:
                self.insertGuildClan(guild_id, clan_tag)
            return True
        # For some reason it returns an error [near ".": syntax error] even if it successfully updated/inserted,
        # need to look into that
        except sqlite3.Error as er:
            print(er)
            return True

    def updateExistingGuildClan(self, guild_id, clan_tag):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("UPDATE clans SET clans.clan = ?"
                    "WHERE clans.guildId = ?;", [clan_tag, guild_id])

    def insertGuildClan(self, guild_id, clan_tag):
        self.reconnect()

        cur = self.con.cursor()
        cur.execute("INSERT INTO clans VALUES (?, ?);", [guild_id, clan_tag])

        self.con.commit()
        self.con.close()

    # Idk, you need to close connection after each query to avoid confusion so there's that workaround
    def reconnect(self):
        self.con = sqlite3.connect('db/main.db')

    def __init__(self):
        self.con = sqlite3.connect('db/main.db')
        self.con.close()