import discord
from discord.ext import commands
from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot, Context

from utils.data_tools import conversion, operation
from utils.check import check, check_list
from utils.render_tools import render_factory


class NameCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    @app_commands.command()
    @check()
    async def act(self, context: Context|Interaction):
        ...

async def setup(bot: Bot):
    await bot.add_cog(NameCog(bot))