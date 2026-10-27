from discord.ext.commands import Context
from discord import Interaction, User, Member, Message, Guild
from discord import TextChannel, VoiceChannel, StageChannel, CategoryChannel, ForumChannel, Thread, DMChannel, GroupChannel
from beartype import beartype


Channel = (TextChannel|VoiceChannel|StageChannel|CategoryChannel|ForumChannel|Thread|DMChannel|GroupChannel)

@beartype
class UniferContext:
    """
    A class for combining two context objects.
    """

    __slots__ = ("source", "user", "message", "channel", "guild")

    def __init__(self, source: Context|Interaction):
        self.source = source

        self.user: Member|User|None = getattr(source, "author", None) or getattr(source, "user", None)
        self.message: Message|None = getattr(source, "message", None)
        self.channel: Channel|None = getattr(source, "channel", None)
        self.guild: Guild|None = getattr(source, "guild", None)