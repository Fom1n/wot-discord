from discord import SelectOption
from discord.ui import Select, View


class Region:

    async def callback(self, interaction):
        guild_id = interaction.guild_id
        self.region = interaction.data['values'][0]
        self.update_view()
        await interaction.response.edit_message(view=self.view)
        if self.view is None or self.region is None or self.db_handler is None:
            await interaction.channel.send(self.get_nok_message())
            return
        success = await self.set_region(guild_id, self.region)
        if not success:
            await interaction.channel.send(self.get_nok_message())
        else:
            await interaction.channel.send("Success! Region - " + self.region)

    def get_nok_message(self):
        return "Sorry, something went wrong."

    async def set_region(self, guild_id, region):
        return self.db_handler.updateRegion(guild_id, region)

    def update_view(self):
        children = self.view.children
        for child in children:
            if child.custom_id == "region":
                child.disabled = True

    def set_view(self, view):
        self.view = view

    def __init__(self, db_handler):
        self.region = None
        self.db_handler = db_handler
        self.view = None


def create_region_view(db_handler):
    region = Region(db_handler)
    select_region = Select(
        custom_id="region",
        placeholder="Select your region",
        options=create_region_options()
    )
    select_region.callback = region.callback
    view = View()
    view.add_item(select_region)
    region.set_view(view)
    return view

def create_region_options():
    selects = []
    for region in regions_map:
        selects.append(
            SelectOption(
                label=region,
                value=regions_map[region]
            )
        )
    return selects

regions_map = {
    'RU region': 'ru',
    'EU region': 'eu'
}