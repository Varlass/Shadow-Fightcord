import discord
from discord.ext import commands
from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot, Context

from utils.check import check, check_list


class NameCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    @check()
    async def text(self, ctx: Context):
        ...


    @app_commands.command()
    async def slash(self, interaction: Interaction):
        ...

async def setup(bot: Bot):
    await bot.add_cog(NameCog(bot))