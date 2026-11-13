from discord import Guild, Intents
from discord.ext.commands import Bot, Context, CommandError, CommandNotFound, CheckFailure, BotMissingPermissions, when_mentioned_or
from pathlib import Path
from importlib import import_module
from dotenv import load_dotenv
from os import getenv
load_dotenv()

from data.manager import DIR, DefaultData
DefaultData(DIR / "default_data").init_files()
from lib.check import check_list
from lib.logger import logger

from src.data_manager import DataManager


class MyBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = DataManager()

    async def on_ready(self):
        for guild in self.guilds:
            if guild.id in set(check_list["Guilds"].values()):
                continue
            await guild.leave()


    async def on_guild_join(self, guild: Guild):
        if guild.id in set(check_list["Guilds"].values()):
            return
        await guild.leave()


    async def on_command_error(self, ctx: Context, error: CommandError):
        error = getattr(error, "original", error) # If CommandInvokeError.

        if isinstance(error, (CommandNotFound, CheckFailure)):
            return

        if isinstance(error, BotMissingPermissions):
            await ctx.reply("У меня недостаточно прав для выполнения команды.", mention_author = False, delete_after = 10)
            return

        await ctx.send(f"Unknown error.\n<@{check_list["Members"]["Developer"]}>")
        logger(error)


    async def setup_hook(self):
        root = Path(__file__).resolve().parent

        for file in (root / "src/cogs").rglob("*.py"):
            if file.name.startswith("_"):
                continue

            module_name = ".".join(file.relative_to(root).with_suffix("").parts)

            try:
                module = import_module(module_name)
                
                if hasattr(module, "setup"):
                    await module.setup(self)

            except Exception as error:
                logger(error)


TOKEN = getenv("TOKEN")

prefix = when_mentioned_or("c!", "C!")

intents = Intents().default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = MyBot(command_prefix = prefix, intents = intents, help_command = None, case_insensitive = True)


if __name__ == "__main__":
    try:
        bot.data.start()
        bot.run(TOKEN)

    finally:
        bot.data.end()