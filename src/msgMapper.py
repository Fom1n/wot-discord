class MessageMapper:

    async def mapMessage(self, msg):
        # let's ignore our own messages for now
        if msg.author.id == self.client.user.id:
            return

        if msg.content.startswith('$hello'):
            await msg.channel.send('Hi!')
        if msg.content.startswith('$setclan'):
            await self.setClanHandler(msg)

    # TODO: Check with WG api if the clan actually exists to prevent stupid situations
    async def setClanHandler(self, msg):
        arr = msg.content.split(" ")
        if len(arr) < 2 | len(arr) > 2:
            await msg.channel.send("You need to specify clan after space, like this - '$setclan FAME' ")
        else:
            inserted = self.db_handler.updateGuildClan(int(msg.author.guild.id), arr[1])
            if inserted:
                await msg.channel.send("Successfully updated your clan tag to [" + arr[1] + "]!")
            else:
                await msg.channel.send("Could not update your clan tag for some reason. Please try again later.")

    def __init__(self, client, db_handler):
        self.client = client
        self.db_handler = db_handler
        pass
