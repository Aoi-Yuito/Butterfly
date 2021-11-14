import time
import typing as t
from string import ascii_lowercase

import hikari
import lightbulb

from bluebrain.bot import Blue_Bot
from bluebrain.utils import checks, chron, string

MODULE_NAME = "warn"

MIN_POINTS = 1
MAX_POINTS = 20
MAX_WARNTYPE_LENGTH = 25
MAX_WARNTYPES = 25


class Warn(lightbulb.Plugin):
    """A system to serve official warnings to members."""

    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        self.configurable: bool = True
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)


    @lightbulb.group(
        name="warn",
        insensitive_commands=True,
        inherit_checks=True
    )
    #@checks.module_has_initialised(MODULE_NAME)
    #@checks.author_can_warn()
    async def warn_group(
        self,
        ctx,
        targets: lightbulb.converters.Greedy[hikari.Member],
        warn_type: str,
        points_override: t.Optional[int],
        *,
        comment: t.Optional[str],
    ):
        """Warns one or more members in your server."""
        if not targets:
            return await ctx.respond(f"{(await self.bot.cross)} No valid targets were passed.")

        if any(c not in ascii_lowercase for c in warn_type):
            return await ctx.respond(f"{(await self.bot.cross)} Warn type identifiers can only contain lower case letters.")

        if (points_override is not None) and (not MIN_POINTS <= points_override <= MAX_POINTS):
            return await ctx.respond(
                f"{(await self.bot.cross)} The specified points override must be between {MIN_POINTS} and {MAX_POINTS} inclusive."
            )

        if (comment is not None) and len(comment) > 256:
            return await ctx.respond(f"{(await self.bot.cross)} The comment must not exceed 256 characters in length.")

        type_map = {
            warn_type: points
            for warn_type, points in await self.bot.db.records(
                "SELECT WarnType, Points FROM warntypes WHERE GuildID = ?", ctx.get_guild().id
            )
        }

        if warn_type not in type_map.keys():
            return await ctx.respond(f"{(await self.bot.cross)} That warn type does not exist.")

        for target in targets:
            if target.bot:
                await ctx.respond(f"{(await self.bot.info)} Skipping {target.display_name} as bots can not be warned.")
                continue

            await self.bot.db.execute(
                "INSERT INTO warns (WarnID, GuildID, UserID, ModID, WarnType, Points, Comment) VALUES (?, ?, ?, ?, ?, ?, ?)",
                self.bot.generate_id(),
                ctx.get_guild().id,
                target.id,
                ctx.author.id,
                warn_type,
                points_override or type_map[warn_type],
                comment,
            )

            records = await self.bot.db.records(
                "SELECT WarnType, Points FROM warns WHERE GuildID = ? AND UserID = ?", ctx.get_guild().id, target.id
            )
            max_points, max_strikes = (
                await self.bot.db.record("SELECT MaxPoints, MaxStrikes FROM warn WHERE GuildID = ?", ctx.get_guild().id)
                or [None] * 2
            )

            if (wc := [r[0] for r in records].count(warn_type)) >= (max_strikes or 3):
                # Account for unbans.
                await target.ban(reason=f"Received {string.ordinal(wc)} warning for {warn_type}.")
                return await ctx.respond(
                    f"{(await self.bot.info)} {target.display_name} was banned because they received a {string.ordinal(wc)} warning for the same offence."
                )

            points = sum(r[1] for r in records)

            if points >= (max_points or 12):
                await target.ban(reason=f"Received equal to or more than the maximum allowed number of points.")
                return await ctx.respond(
                    f"{(await self.bot.info)} {target.display_name} was banned because they received equal to or more than the maximum allowed number of points."
                )

            await ctx.respond(
                f"{target.mention}, you have been warned for {warn_type} for the {string.ordinal(wc)} of {max_strikes or 3} times. You now have {points} of your allowed {max_points or 12} points."
            )



    @warn_group.command(name="remove", aliases=["rm"])
    #@checks.module_has_initialised(MODULE_NAME)
    #@checks.author_can_warn()
    async def warn_remove_command(self, ctx, warn_id: str):
        """Removes a warning."""
        modified = await self.bot.db.execute("DELETE FROM warns WHERE WarnID = ?", warn_id)

        if not modified:
            return await ctx.respond(f"{(await self.bot.cross)} That warn ID is not valid.")

        await ctx.respond(f"{(await self.bot.tick)} Warn {warn_id} removed.")


    @warn_group.command(name="reset")
    #@checks.module_has_initialised(MODULE_NAME)
    #@commands.has_permissions(administrator=True)
    async def warn_reset_command(self, ctx, target: hikari.Member):
        """Resets a member's warnings."""
        modified = await self.bot.db.execute(
            "DELETE FROM warns WHERE GuildID = ? AND UserID = ?", ctx.get_guild().id, target.id
        )

        if not modified:
            return await ctx.respond(f"{(await self.bot.cross)} That member does not have any warns.")

        await ctx.respond(f"{(await self.bot.tick)} Warnings for {target.display_name} reset.")


    @warn_group.command(name="list")
    #@checks.module_has_initialised(MODULE_NAME)
    async def warn_list_command(self, ctx, target: t.Optional[t.Union[hikari.Member, str]]):
        """Lists a member's warnings."""
        target = target or ctx.author

        if isinstance(target, str):
            return await ctx.respond(
                f"{(await self.bot.cross)} Blue Brain was unable to identify a member with the information provided."
            )

        records = await self.bot.db.records(
            "SELECT WarnID, ModID, WarnTime, WarnType, Points, Comment FROM warns WHERE GuildID = ? AND UserID = ? ORDER BY WarnTime DESC",
            ctx.get_guild().id,
            target.id,
        )
        points = sum(record[4] for record in records)

        await ctx.respond(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Warn",
                title=f"Warn information for {target.username}",
                description=f"{points} point(s) accumulated. Showing {min(len(records), 10)} of {len(records)} warning(s).",
                colour=target.get_top_role().color,
                thumbnail=target.avatar_url,
                fields=(
                    (
                        record[0],
                        f"**{record[3]}**: {record[5] or 'No additional comment was made.'} ({record[4]} point(s))\n"
                        f"{getattr(ctx.guild.get_member(record[1]), 'mention', 'Unknown')} - {chron.short_date_and_time(chron.from_iso(record[2]))}",
                        False,
                    )
                    for record in records[-10:]
                ),
            )
        )



def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Warn(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Warn")
