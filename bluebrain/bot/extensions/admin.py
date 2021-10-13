import hikari
import lightbulb

from bluebrain.bot import Blue_Bot

class Admin(lightbulb.Plugin):
    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)


    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="shutdown", aliases=["sd"])
    async def shutdown_command(self, ctx: lightbulb.Context) -> None:
        await ctx.bot.close()


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Admin(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Admin")