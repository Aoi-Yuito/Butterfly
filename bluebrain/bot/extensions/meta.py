import hikari
import lightbulb

from time import time
from bluebrain.utils import checks
from bluebrain.bot import Blue_Bot

class Meta(lightbulb.Plugin):
    """Commands for retrieving information regarding Solaris, from invitation links to detailed bot statistics."""
    
    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="ping")
    async def ping_command(self, ctx: lightbulb.Context) -> None:
        lat = self.bot.heartbeat_latency * 1_000
        s = time()
        pm = await ctx.respond(f"{self.bot.info} Pong! DWSP latency: {lat:,.0f} ms. Response time: - ms.")
        e = time()
        await pm.edit(
            content=f"{self.bot.info} Pong! DWSP latency: {lat:,.0f} ms. Response time: {(e-s)*1_000:,.0f} ms."
        )


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="source", aliases=["src"])
    async def source_command(self, ctx: lightbulb.Context) -> None:
        await ctx.respond(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Information",
                thumbnail=self.bot.get_me().avatar_url,
                fields=(
                    (
                        "Available under the GPLv3 license",
                        "Click [here](https://github.com/parafoxia/Solaris) to view.",
                        False,
                    ),
                ),
            )
        )


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="h")
    async def h_command(self, ctx: lightbulb.Context) -> None:
        """get help text"""
        #await ctx.send_help(ctx.command)  
        #help_text = lightbulb.get_help_text(self.h_command)
        #await ctx.respond(help_text)
        
        #from bluebrain.utils.modules import retrieve
        #await ctx.respond((await retrieve.log_channel(ctx.bot, ctx.get_guild().id)))
        
        #bot = await self.bot.rest.fetch_member(ctx.get_guild().id, 841547626772168704)
        #perm = lightbulb.utils.permissions_for(bot)
        #print(perm.ADMINISTRATOR)

        #async with ctx.get_channel().trigger_typing():
        #    msg = await ctx.respond("test")
        #    emoji = []
        #    emoji.append(ctx.bot.cache.get_emoji(832160810738253834))
        #    emoji.append(ctx.bot.cache.get_emoji(832160894079074335))   
        #    for em in emoji:
        #await msg.add_reaction(em)

        #perm = lightbulb.utils.permissions_in(
        #    ctx.get_channel(),
        #    await ctx.bot.rest.fetch_member(
        #        ctx.get_guild().id,
        #        841547626772168704
        #    ),
        #    True
        #)
        #if not perm:
        #    print(perm.SEND_MESSAGES)

        #perm = lightbulb.utils.permissions_for(
        #    await ctx.bot.rest.fetch_member(
        #        ctx.get_guild().id,
        #        841547626772168704
        #    )
        #)
        #print(perm)
        #for ext in self.bot._extensions:
        #    await ctx.respond(self.bot.get_plugin(ext.title()))



def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Meta(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Meta")
