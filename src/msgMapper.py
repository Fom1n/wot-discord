class MessageMapper:

    async def mapMessage(self, msg):
        if msg.content.startswith('$hello'):
            await msg.channel.send('Hello there!')

    def __init__(self, client):
        self.client = client
        pass
