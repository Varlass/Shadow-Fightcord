from discord.ext import commands
from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot, Context

from cogs.window_create.window_manager import window_create


class NameCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    @app_commands.command()
    async def act(self, context: Context|Interaction):
        message = await window_create(self, context, "MAIN")
        await context.channel.send(**message)


async def setup(bot: Bot):
    await bot.add_cog(NameCog(bot))