# init script and sql sandbox (sqlite is a single-file database, you can't run queries from cmd like with postgres)

import sqlite3

con = sqlite3.connect('main.db')

cur = con.cursor()

# cur.execute('''CREATE TABLE clans (guildId INTEGER, clan TEXT, clanId INTEGER);''')
# cur.execute('''INSERT INTO clans VALUES (819552499211042856, 'GIFTD', 500075427)''')

# cur.execute('''CREATE TABLE channels (guildId INTEGER, type TEXT, channelId INTEGER)''')
# guild_id = 819552499211042856
# channel_id = 883506039205535784
# cur.execute("UPDATE channels SET channelId = ? WHERE guildId = ?", [channel_id, guild_id])
#
# guild_id = 819552499211042856
# clan_tag = "FAME"
print(cur.execute("select * FROM CHANNELS").fetchall())
# cur.execute("UPDATE clans SET clan = ? WHERE clans.guildId = ?", [clan_tag, guild_id])
# cur.execute('DELETE FROM clans WHERE clans.guildId = ?', [guild_id])
con.commit()
con.close()
# for row in cur.execute('SELECT EXISTS(SELECT 1 FROM clans WHERE clans.guildId = ?)', [guildid]):
#     print(row[0])
