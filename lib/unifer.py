from discord.ext.commands import Context, Bot, Command
from discord import Interaction, Member, User, Client, Guild, Message, InteractionResponse, Webhook, Locale, Permissions
from discord.abc import Messageable
from functools import wraps
from typing import Any, TYPE_CHECKING
from datetime import datetime


__all__ = ["unifer", "UniferContext"]


class UniferMeta(type):
    def __instancecheck__(cls, instance):
        return issubclass(type(instance) is cls)

class UniferContext(metaclass = UniferMeta):
    """
    The class for unification 'discord.ext.commands.Context' and 'discord.Interaction' objects.
    """

    if TYPE_CHECKING:
        channel: Messageable|None
        guild: Guild|None
        message: Message|None
        command: Command[Any, Any, Any]

        prefix: str
        invoked_with: str
        invoked_subcommand: str|None
        args: list[Any]
        kwargs: dict[str, Any]
        cog: Any
        retry_after: float|None

        response: InteractionResponse
        followup: Webhook
        token: str
        locale: Locale
        guild_locale: Locale|None
        app_permissions: Permissions
        command_id: int|None
        created_at: datetime


    __slots__ = ("_source", "bot", "author")

    def __init__(self, source: Context|Interaction):
        self._source = source

        self.bot: Bot|Client = getattr(source, "bot", None) or getattr(source, "client", None)
        self.author: Member|User = getattr(source, "author", None) or getattr(source, "user", None)


    @property
    def client(self) -> Bot|Client:
        return self.bot

    @property
    def user(self) -> Member|User:
        return self.author


    @property
    def __class__(self) -> type:
        return type(self._source)

    def __getattr__(self, name: str) -> Any:
        if name == "_source":
            raise AttributeError(name)

        return getattr(self._source, name)


def unifer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        found: bool = False
        new_args: list[Any] = list(args)

        for index, arg in enumerate(new_args):
            if found == False and isinstance(arg, (Context, Interaction)):
                arg[index] = UniferContext(arg)
                found = True
                break

        if found == False:
            for name, value in kwargs.items():
                if isinstance(value, (Context, Interaction)):
                    kwargs[name] = UniferContext(value)
                    break

        return func(*new_args, **kwargs)
    return wrapper