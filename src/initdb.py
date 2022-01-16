# init script and sql sandbox (sqlite is a single-file database, you can't run queries from cmd like with postgres)

import sqlite3
con = sqlite3.connect('db/main.db')

cur = con.cursor()
#
# cur.execute('''CREATE TABLE clans (guildId INTEGER, clan TEXT)
# ''')
#
# # some guild (my test guild)
# cur.execute('''INSERT INTO clans VALUES (819552499211042856, 'GIFTD')
# ''')
#
# con.commit()
#
# con.close()
guild_id = 819552499211042856
clan_tag = "FAME"

# cur.execute("UPDATE clans SET clan = ? WHERE clans.guildId = ?", [clan_tag, guild_id])
# cur.execute("DELETE FROM clans WHERE clans.guildId = ?", [guild_id])
# con.commit()
# con.close()
print(cur.execute('SELECT * FROM clans WHERE clans.guildId = ?', [guild_id]).fetchall())
# for row in cur.execute('SELECT EXISTS(SELECT 1 FROM clans WHERE clans.guildId = ?)', [guildid]):
#     print(row[0])