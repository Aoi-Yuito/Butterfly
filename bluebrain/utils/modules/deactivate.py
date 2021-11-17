import hikari

from bluebrain.utils.modules import retrieve


async def gateway(ctx):
    async with ctx.typing():
        active, rc_id, gm_id = await ctx.bot.db.record(
            "SELECT Active, RulesChannelID, GateMessageID FROM gateway WHERE GuildID = ?", ctx.get_guild().id
        )

        if not active:
            await ctx.respond(f"{ctx.bot.cross} The gateway module is already inactive.")
        else:
            try:
                gm = await ctx.bot.cache.get_guild_channel(rc_id).fetch_message(gm_id)
                await gm.delete()
            except (hikari.NotFoundError, discord.ForbiddenError, AttributeError):
                pass

            await ctx.bot.db.execute("DELETE FROM entrants WHERE GuildID = ?", ctx.get_guild().id)
            await ctx.bot.db.execute(
                "UPDATE gateway SET Active = 0, GateMessageID = NULL WHERE GuildID = ?", ctx.get_guild().id
            )

            await ctx.respond(f"{ctx.bot.tick} The gateway module has been deactivated.")
            lc = await retrieve.log_channel(ctx.bot, ctx.get_guild().id)
            await lc.send(f"{ctx.bot.info} The gateway module has been deactivated.")


async def everything(ctx):
    await gateway(ctx)
