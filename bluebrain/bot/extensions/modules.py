import typing as t

import hikari
import lightbulb

from bluebrain.bot import Blue_Bot
from bluebrain.utils import ERROR_ICON, LOADING_ICON, SUCCESS_ICON, checks, menu, modules


class SetupMenu(menu.SelectionMenu):
    def __init__(self, ctx):
        pagemap = {
            "header": "Setup Wizard",
            "title": "Hello!",
            "description": "Welcome to the Solaris first time setup! You need to run this before you can use most of Solaris' commands, but you only ever need to run once.\n\nIn order to operate effectively in your server, Solaris needs to create a few things:",
            "thumbnail": ctx.bot.get_me().avatar_url,
            "fields": (
                (
                    "A log channel",
                    "This will be called solaris-logs and will be placed directly under the channel you run the setup in. This channel is what Solaris will use to communicate important information to you, so it is recommended you only allow server moderators access to it. You will be able to change what Solaris uses as the log channel later.",
                    False,
                ),
                (
                    "An admin role",
                    "This will be called Solaris Administrator and will be placed at the bottom of the role hierarchy. This role does not provide members any additional access to the server, but does allow them to use Solaris' configuration commands. Server administrators do not need this role to configure Solaris. You will be able to change what Solaris uses as the admin role later.",
                    False,
                ),
                (
                    "Ready?",
                    f"If you are ready to run the setup, select {ctx.bot.tick}. To exit the setup without changing anything select {ctx.bot.cross}.",
                    False,
                ),
            ),
        }
        super().__init__(ctx, ["832160810738253834", "832160894079074335"], pagemap, timeout=120.0)

    async def start(self):
        r = await super().start()
        print(r.emoji_name)

        if r.emoji_name == "confirm" and r.user_id == self.ctx.author.id:# and r.message_id == self.ctx.message.id:
            pagemap = {
                "header": "Setup Wizard",
                "description": "Please wait... This should only take a few seconds.",
                "thumbnail": LOADING_ICON,
            }
            await self.switch(pagemap, remove_all_reactions=True)
            await self.run()
        elif r == "cancel" and r.user_id == self.ctx.author.id:# and r.message_id == self.ctx.message.id:
            await self.stop()

    async def run(self):
        if not await modules.retrieve.system__logchannel(self.bot, self.ctx.get_guild().id):
            perm = lightbulb.utils.permissions_for(
                await self.bot.rest.fetch_member(
                    self.ctx.get_guild().id,
                    841547626772168704
                )
            )
            if perm.MANAGE_CHANNELS:
                lc = await self.create_text_channel(
                    name="solaris-logs",
                    category=self.ctx.get_channel().parent_id,
                    position=self.ctx.get_channel().position,
                    topic=f"Log output for {self.ctx.guild.me.mention}",
                    reason="Needed for Solaris log output.",
                )
                await self.bot.db.execute(
                    "UPDATE system SET DefaultLogChannelID = ?, LogChannelID = ? WHERE GuildID = ?",
                    lc.id,
                    lc.id,
                    self.ctx.get_guild().id,
                )
                await lc.send(f"{self.bot.tick} The log channel has been created and set to {lc.mention}.")
            else:
                pagemap = {
                    "header": "Setup Wizard",
                    "title": "Setup failed",
                    "description": "The log channel could not be created as Solaris does not have the Manage Channels permission. The setup can not continue.",
                    "thumbnail": ERROR_ICON,
                }
                await self.switch(pagemap)
                return

        if not await modules.retrieve.system__adminrole(self.bot, self.ctx.get_guild().id):
            perm = lightbulb.utils.permissions_for(
                await self.bot.rest.fetch_member(
                    self.ctx.get_guild().id,
                    841547626772168704
                )
            )
            if perm.MANAGE_ROLES:
                ar = await self.rest.create_role(
                    guild=self.ctx.get_guild().id,
                    name="Solaris Administrator",
                    permissions=hikari.Permissions(value=0),
                    reason="Needed for Solaris configuration.",
                )
                await self.bot.db.execute(
                    "UPDATE system SET DefaultAdminRoleID = ?, AdminRoleID = ? WHERE GuildID = ?",
                    ar.id,
                    ar.id,
                    self.ctx.get_guild().id,
                )
                await lc.send(f"{self.bot.tick} The admin role has been created and set to {ar.mention}.")
            else:
                pagemap = {
                    "header": "Setup Wizard",
                    "title": "Setup failed",
                    "description": "The admin role could not be created as Solaris does not have the Manage Roles permission. The setup can not continue.",
                    "thumbnail": ERROR_ICON,
                }
                await self.switch(pagemap)
                return

        await self.complete()

    async def configure_modules(self):
        await self.complete()

    async def complete(self):
        pagemap = {
            "header": "Setup",
            "title": "First time setup complete",
            "description": "Congratulations - the first time setup has been completed! You can now use all of Solaris' commands, and activate all of Solaris' modules.\n\nEnjoy using Solaris!",
            "thumbnail": SUCCESS_ICON,
        }
        await modules.config.system__runfts(self.bot, self.ctx.get_channel(), 1)
        await self.switch(pagemap, clear_reactions=True)


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
    @lightbulb.command(name="setup")
    #@checks.bot_has_booted()
    #@checks.first_time_setup_has_not_run()
    #@checks.author_can_configure()
    #@checks.guild_is_not_discord_bot_list()
    async def setup_command(self, ctx):
        """Runs the first time setup."""
        await SetupMenu(ctx).start()


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(
        name="config",
        aliases=["set"]
    )
    #@checks.bot_has_booted()
    #@checks.first_time_setup_has_run()
    #@checks.author_can_configure()
    async def config_command(
        self,
        ctx,
        module: str,
        attr: str,
        #objects: lightbulb.commands.base.OptionModifier.Greedy[t.Union[hikari.GuildTextChannel, hikari.Role]],
        *,
        text: t.Optional[t.Union[int, str]],
    ):
        """Configures Solaris; use `help config` to bring up a special help menu."""
        if module.startswith("_") or attr.startswith("_"):
            await ctx.respond(f"{self.bot.cross} The module or attribute you are trying to access is non-configurable.")
        elif (func := getattr(modules.config, f"{module}__{attr}", None)) is not None:
            await func(self.bot, ctx.get_channel(), (objects[0] if len(objects) == 1 else objects) or text)
        else:
            await ctx.respond(f"{self.bot.cross} Invalid module or attribute.")


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


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(
        name="activate",
        aliases=["enable"]
    )
    #@checks.bot_is_ready()
    #@checks.log_channel_is_set()
    #@checks.first_time_setup_has_run()
    #@checks.author_can_configure()
    async def activate_command(self, ctx, module: str):
        """Activates a module."""
        if module.startswith("_"):
            await ctx.respond(f"{self.bot.cross} The module you are trying to access is non-configurable.")
        elif (func := getattr(modules.activate, module, None)) is not None:
            await func(ctx)
        else:
            await ctx.respond(f"{self.bot.cross} That module either does not exist, or can not be activated.")


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(
        name="deactivate",
        aliases=["disable"]
    )
    #@checks.bot_is_ready()
    #@checks.log_channel_is_set()
    #@checks.first_time_setup_has_run()
    #@checks.author_can_configure()
    async def deactivate_command(self, ctx, module: str):
        """Deactivates a module."""
        if module.startswith("_"):
            await ctx.respond(f"{self.bot.cross} The module you are trying to access is non-configurable.")
        elif (func := getattr(modules.deactivate, module, None)) is not None:
            await func(ctx)
        else:
            await ctx.respond(f"{self.bot.cross} That module either does not exist, or can not be deactivated.")


    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(
        name="restart"
    )
    #@checks.bot_is_ready()
    #@checks.log_channel_is_set()
    #@checks.first_time_setup_has_run()
    #@checks.author_can_configure()
    async def restart_command(self, ctx, module: str):
        """Restarts a module. This is a shortcut command which calls `deactivate` then `activate`."""
        if module.startswith("_"):
            await ctx.respond(f"{self.bot.cross} The module you are trying to access is non-configurable.")
        elif (dfunc := getattr(modules.deactivate, module, None)) is not None and (
            afunc := getattr(modules.activate, module, None)
        ) is not None:
            await dfunc(ctx)
            await afunc(ctx)
        else:
            await ctx.respond(f"{self.bot.cross} That module either does not exist, or can not be restarted.")


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Modules(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Modules")
