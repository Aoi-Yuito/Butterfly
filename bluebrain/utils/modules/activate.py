import lightbulb

from bluebrain.utils.modules import retrieve


async def gateway(ctx):
    async with ctx.get_channel().trigger_typing():
        active, rc_id, br_id, gt = (
            await ctx.bot.db.record(
                "SELECT Active, RulesChannelID, BlockingRoleID, GateText FROM gateway WHERE GuildID = ?", ctx.get_guild().id
            )
            or [None] * 4
        )

        perm = lightbulb.utils.permissions_for(
            await ctx.bot.rest.fetch_member(
                ctx.get_guild().id,
                841547626772168704
            )
        )

        if active:
            await ctx.repond(f"{ctx.bot.cross} The gateway module is already active.")
        elif not (perm.MANAGE_ROLES and perm.KICK_MEMBERS):
            await ctx.respond(
                f"{ctx.bot.cross} The gateway module could not be activated as Solaris does not have the Manage Roles and Kick Members permissions."
            )
        elif (rc := ctx.bot.cache.get_guild_channel(rc_id)) is None:
            await ctx.respond(
                f"{ctx.bot.cross} The gateway module could not be activated as the rules channel does not exist or can not be accessed by Solaris."
            )
        elif ctx.bot.cache.get_role(br_id) is None:
            await ctx.respond(
                f"{ctx.bot.cross} The gateway module could not be activated as the blocking role does not exist or can not be accessed by Solaris."
            )
        else:
            gm = await rc.send(
                gt
                or f"**Attention:** Do you accept the rules outlined above? If you do, select {ctx.bot.emoji.mention('confirm')}, otherwise select {ctx.bot.emoji.mention('cancel')}."
            )
            
            emoji = []
            emoji.append(ctx.bot.cache.get_emoji(832160810738253834))
            emoji.append(ctx.bot.cache.get_emoji(832160894079074335))
            
            for em in emoji:
                await gm.add_reaction(em)

            await ctx.bot.db.execute(
                "UPDATE gateway SET Active = 1, GateMessageID = ? WHERE GuildID = ?", gm.id, ctx.get_guild().id
            )
            await ctx.respond(f"{ctx.bot.tick} The gateway module has been activated.")
            lc = await retrieve.log_channel(ctx.bot, ctx.get_guild().id)
            await lc.send(f"{ctx.bot.info} The gateway module has been activated.")

