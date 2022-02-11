# init script and sql sandbox (sqlite is a single-file database, you can't run queries from cmd like with postgres)

import sqlite3

con = sqlite3.connect('db/main.db')

cur = con.cursor()

# cur.execute('''CREATE TABLE clans (guildId INTEGER, clan TEXT, clanId INTEGER);''')
# cur.execute('''CREATE TABLE region (guildId INTEGER PRIMARY KEY, region TEXT);''')
# cur.execute('''CREATE TABLE channels (guildId INTEGER, channelId INTEGER, type TEXT, clan TEXT, region TEXT, PRIMARY KEY (guildId, channelId));''')
# cur.execute('''CREATE TABLE clan_to_id (clan TEXT, clanId INTEGER, region TEXT, PRIMARY KEY (clan, region))''')
# cur.execute('DELETE FROM channels WHERE guildId=366915317496152075')
# print(cur.execute('SELECT * from channels;').fetchall())
# cur.execute('''INSERT into channels VALUES(819552499211042856, 940304860052602891, 'PFP', 'GIFTD', 'eu')''')
print(cur.execute('SELECT * FROM region').fetchall())
# guild_id = 819552499211042856
# channel_id = 883506039205535784
# cur.execute("UPDATE channels SET channelId = ? WHERE guildId = ?", [channel_id, guild_id])
# cur.execute('''UPDATE REGION SET region = 'eu' WHERE guildId = 819552499211042856''')
# print(cur.execute('delete from region where guildId = 819552499211042856').fetchall())
# cur.execute('''drop table channels''')

# cur.execute('''INSERT INTO channels VALUES (819552499211042856, 1, 'sh', 'MERCY', 'ru')''')
# print(cur.execute('''select * from channels''').fetchall())
# guild_id = 819552499211042856
# clan_tag = "FAME"
# print(cur.execute("select * FROM CHANNELS where guildId = ").fetchall())
# cur.execute("UPDATE clans SET clan = ? WHERE clans.guildId = ?", [clan_tag, guild_id])
# cur.execute('DELETE FROM clans WHERE clans.guildId = ?', [guild_id])
con.commit()
con.close()
# for row in cur.execute('SELECT EXISTS(SELECT 1 FROM clans WHERE clans.guildId = ?)', [guildid]):
#     print(row[0])
