import hikari
import lightbulb

from bluebrain.bot import Blue_Bot

class System(lightbulb.Plugin):
    """System attributes."""

    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        self.configurable: bool = True
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="prefix")
    async def prefix_command(self, ctx: lightbulb.Context) -> None:
        """Displays Blue Brain's prefix in your server. Note that mentioning Blue Brain will always work."""
        prefix = await self.bot.prefix(ctx.get_guild().id)
        await ctx.send("fdsf")
        await ctx.respond(
            f"{(await self.bot.info)} Blue Brain's prefix in this server is {prefix}. To change it, use `{prefix}config system prefix <new prefix>`."
        )


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(System(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("System")