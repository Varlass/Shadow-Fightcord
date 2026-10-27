from discord import Interaction
from discord.ext.commands import Context, CheckFailure, check as ch
from beartype import beartype

from data.manager import FileManager
from utils.logger import logger
from utils.unifer import UniferContext


check_list: dict[str, int|dict[str, str]] = FileManager("id_list.yaml").read()

try:
    white_list: set[int] = {check_list[category][name] for category, names in check_list["White_List"].items() for name in names if name}

except KeyError as error:
    white_list: set = set()
    logger(error)


@beartype
def check(checks: set[int]|int = set(), *, bypass: bool = True): # Декоратор проверки id.
    if isinstance(checks, int):
        checks = {checks}

    checks = checks|white_list if bypass else checks

    async def wrapper(source: Context|Interaction) -> bool:
        context = UniferContext(source)

        ids = {context.user.id,
               *{role.id for role in context.user.roles},
               context.channel.id,
               context.guild.id,
               context.guild.owner_id}
        
        ids.discard(None)

        if ids & checks:
            return True

        raise CheckFailure()

    return ch(wrapper)