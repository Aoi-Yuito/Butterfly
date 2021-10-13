import hikari
import lightbulb

from time import time
import typing as t
from bluebrain.utils import Search
from bluebrain.utils import checks, converters
from bluebrain.bot import Blue_Bot

class Meta(lightbulb.Plugin):
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
        pm = await ctx.respond(f"{(await self.bot.info)} Pong! DWSP latency: {lat:,.0f} ms. Response time: - ms.")
        e = time()
        await pm.edit(
            content=f"{(await self.bot.info)} Pong! DWSP latency: {lat:,.0f} ms. Response time: {(e-s)*1_000:,.0f} ms."
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
        await ctx.send_help(ctx.command)  
        help_text = lightbulb.get_help_text(self.h_command)
        await ctx.respond(help_text)


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="m")
    async def m_command(self, ctx: lightbulb.Context, target: t.Optional[t.Union[hikari.Member, converters.SearchedMember, str]], name: str) -> None:
        async def grab(x):
            person = await ctx.bot.rest.fetch_user(x)
            return person.username
        lists = []
        for m in ctx.get_guild().get_members():
            lists.append((await ctx.bot.rest.fetch_user(m)))
        print(lists)
        if (member := converters.get(
                lists,
                username=str(Search(name, [(await grab(m)) for m in ctx.get_guild().get_members()]).best(min_accuracy=0.75)),
            )) is not None:
            print(member)
            print(member.username)
            print(member.id)


        


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Meta(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Meta")