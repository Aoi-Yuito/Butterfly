import hikari
import lightbulb
import traceback

import aiofiles
import aiofiles.os

from bluebrain.utils import checks
from bluebrain.bot import Blue_Bot

class Error(lightbulb.Plugin):
    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)

    
    async def error(self, err, guild_id, channel_id, exc_info, *args):
        ref = await self.record_error(err, args, exc_info)
        hub = self.bot.get_plugin("Hub")

        if (sc := getattr(hub, "stdout_channel", None)) is not None:
            if guild_id is not None:
                await sc.send(f"{(await self.bot.cross)} Something went wrong (ref: {ref}).")

        if channel_id is not None:
            if guild_id is not None:
                prefix = await self.bot.prefix(guild_id)
                guild = await self.bot.rest.fetch_guild(guild_id)
                channel = guild.get_channel(channel_id)
                await channel.send(
                    f"{(await self.bot.cross)} Something went wrong (ref: {ref}). Quote this reference in the support server, which you can get a link for by using `{prefix}support`."
                )
            elif guild_id is None:
                await self.bot.rest.create_message(
                    channel=channel_id,
                    content=f"{(await self.bot.cross)} Blue Brain does not support command invokations in DMs."
                )

        raise err

    async def record_error(self, err, obj, exc_info):
        obj = getattr(obj, "message", obj)
        if isinstance(obj, hikari.Message):
            cause = f"{obj.content}\n{obj!r}"
        else:
            cause = f"{obj!r}"

        ref = self.bot.generate_id()

        traceback_info = "".join(traceback.format_exception(*exc_info))

        await self.bot.db.execute(
            "INSERT INTO errors (Ref, Cause, Traceback) VALUES (?, ?, ?)", ref, cause, traceback_info
        )
        return ref


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(name="recallerror", aliases=["err"])
    async def error_command(self, ctx: lightbulb.Context, ref: str) -> None:
        cause, error_time, traceback = await self.bot.db.record(
            "SELECT Cause, ErrorTime, Traceback FROM errors WHERE Ref = ?", ref
        )

        path = f"{self.bot._dynamic}/{ref}.txt"
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            text = f"Time of error:\n{error_time}\n\nCause:\n{cause}\n\n{traceback}"
            await f.write(text)

        await ctx.respond(attachment=hikari.File(path))
        await aiofiles.os.remove(path)


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Error(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Error")
