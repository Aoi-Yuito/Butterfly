import typing as t

import hikari
import lightbulb

from bluebrain.bot import Blue_Bot
from bluebrain.utils import ERROR_ICON, LOADING_ICON, SUCCESS_ICON, checks, menu, modules


class Modules(lightbulb.Plugin):
    """Configure, activate, and deactivate Solaris modules."""

    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        self.configurable: bool = True
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(
        name="retrieve",
        aliases=["get"]
    )
    async def retrieve_command(self, ctx, module: str, attr: str):
        """Retrieves attribute information for a module. Note that the output is raw, so some attributes may appear to have strange or incorrect values when in reality they are fine."""
        if module.startswith("_") or attr.startswith("_"):
            await ctx.respond(f"{self.bot.cross} The module or attribute you are trying to access is non-configurable.")
        elif (func := getattr(modules.retrieve, f"{module}__{attr}", None)) is not None:
            v = await func(self.bot, ctx.get_guild().id)
            value = getattr(v, "mention", v)
            await ctx.respond(f"{self.bot.info} Value of {attr}: {value}")
        else:
            await ctx.respond(f"{self.bot.cross} Invalid module or attribute.")


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Modules(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Modules")
