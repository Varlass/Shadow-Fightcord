from discord import Interaction
from discord.ext.commands import Context

from utils.unifer import Unifer
from utils import render_tools as render
from utils.library import colors

from .buttons_func import VIEW_MAP


async def window_create(self, context: Context|Interaction, window: str):
    ctx = Unifer(context)
    wnd = self.bot.data.windows[window]

    message = render.Message(content = wnd["CONTENT"],
                             embeds = [render.Embed(title = wnd[embed]["TITLE"],
                                                     description = wnd[embed]["DESCRIPTION"],
                                                     color = colors.BLUE) for embed in wnd["EMBEDS"]],
                             view = render.View(timeout = 3600,
                                                buttons = [render.Button(label = wnd[view]["LABEL"],
                                                                         callback = VIEW_MAP[view]["CALLBACK"]) for view in wnd["BUTTONS"]]))

    return render.render(message)