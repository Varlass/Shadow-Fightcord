from discord import Interaction
from discord.ext.commands import Context, CheckFailure, check as ch

from data.manager import FileManage
from utils.unifer import Unifer


check_list: dict[str, int|dict[str, list[str]]] = FileManage("id_list.yaml").read()

try:
    white_list = {check_list[category][name] for category, names in check_list["White_List"].items() for name in names if name}

except (TypeError, KeyError):
    white_list = set()


def check(checks: set[int]|int = set(), *, bypass: bool = True): # Декоратор проверки id.
    if isinstance(checks, int):
        checks = {checks}

    if not isinstance(checks, set):
        raise TypeError("Цель проверки должна быть множеством.")

    effective_checks = checks|white_list if bypass else checks

    async def predicate(source: Context|Interaction) -> bool:
        context = Unifer(source)

        ids = {context.user.id,
               *{role.id for role in context.user.roles},
               context.channel.id,
               context.guild.id}
        
        ids.discard(None)

        if ids & effective_checks:
            return True

        raise CheckFailure()

    return ch(predicate)