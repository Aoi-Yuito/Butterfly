import hikari
import lightbulb

import typing as t
import datetime as dt

from collections import defaultdict

from bluebrain.bot import Blue_Bot

from bluebrain.utils import checks, chron, converters, menu, modules, string


class HelpMenu(menu.MultiPageMenu):
    def __init__(self, ctx, pagemaps):
        super().__init__(ctx, pagemaps, timeout=120.0)


class ConfigHelpMenu(menu.NumberedSelectionMenu):
    def __init__(self, ctx):
        pagemap = {
            "header": "Help",
            "title": "Configuration help",
            "description": "Select the module you want to configure.",
            "thumbnail": ctx.bot.get_me().avatar_url,
        }
        super().__init__(
            ctx,
            [extension.name.lower() for extension in ctx.bot._extensions if getattr(extension, "configurable", False)],
            pagemap,
        )

    async def start(self):
        if (r := await super().start()) is not None:
            await self.display_help(r)

    async def display_help(self, module):
        prefix = await self.bot.prefix(self.ctx.get_guild().id)

        await self.message.remove_all_reactions()
        await self.message.edit(
            embed=self.bot.embed.build(
                ctx=self.ctx,
                header="Help",
                title=f"Configuration help for {module}",
                description=(
                    list(filter(lambda c: c.name.lower() == module, self.bot._extensions)).pop().__doc__
                ),
                thumbnail=self.bot.get_me().avatar_url,
                fields=(
                    (
                        (doc := func.__doc__.split("\n", maxsplit=1))[0],
                        f"{doc[1]}\n`{prefix}config {module} {name[len(module)+2:]}`",
                        False,
                    )
                    for name, func in filter(lambda f: module in f[0], modules.config.__dict__.items())
                    if not name.startswith("_")
                ),
            )
        )


class Help(lightbulb.Plugin):
    """Assistance with using a configuring Solaris."""

    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        super().__init__()


    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)

    @staticmethod
    async def basic_syntax(ctx, cmd, prefix):
        try:
            await cmd.is_runnable(ctx)
            return f"{prefix}{cmd.name}" if cmd.parent is None else f"  ↳ {cmd.name}"
        except lightbulb.errors.CommandError:
            return f"{prefix}{cmd.name} (✗)" if cmd.parent is None else f"  ↳ {cmd.name} (✗)"

    @staticmethod
    def full_syntax(ctx, cmd, prefix):
        invokations = "|".join([cmd.name, *cmd.aliases])
        if (p := cmd.parent) is None:
            return f"```{prefix}{invokations} {cmd.signature}```"
        else:
            p_invokations = "|".join([p.name, *p.aliases])
            return f"```{prefix}{p_invokations} {invokations} {cmd.signature}```"

    @staticmethod
    async def required_permissions(ctx, cmd):
        try:
            await cmd.is_runnable(ctx)
            return "Yes"
        except lightbulb.errors.MissingRequiredPermission as exc:
            print(exc)
            mp = string.list_of([str(perm.replace("_", " ")).title() for perm in exc.missing_perms])
            return f"No - You are missing the {mp} permission(s)"
        except lightbulb.errors.BotMissingRequiredPermission as exc:
            mp = string.list_of([str(perm.replace("_", " ")).title() for perm in exc.missing_perms])
            return f"No - Solaris is missing the {mp} permission(s)"
        #except checks.AuthorCanNotConfigure:
        #    return "No - You are not able to configure Solaris"
        #except commands.CommandError:
        #    return "No - Solaris is not configured properly"

    async def get_command_mapping(self, ctx):
        mapping = defaultdict(list)
        plugins = []

        for extension in self.bot._extensions:
            if extension.__doc__ is not None:
                for cmd in self.bot.get_plugin(extension.title()).walk_commands():
                    if (self.bot.get_plugin(extension.title()).__doc__) is not None:
                    #if (lightbulb.help.get_help_text(self.bot.get_command(cmd.name))) is not None:
                        mapping[extension].append(cmd)

        return mapping

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(
        name="helpt"
    )
    async def helpt_command(self, ctx, *, cmd: t.Optional[t.Union[converters.Command, str]])-> None:
        """Help with anything Solaris. Passing a command name or alias through will show help with that specific command, while passing no arguments will bring up a general command overview."""
        prefix = await self.bot.prefix(ctx.get_guild().id)

        if isinstance(cmd, str):
            await ctx.respond(f"{self.bot.cross} Solaris has no commands or aliases with that name.")

        elif isinstance(cmd, lightbulb.commands.Command):
            if cmd.name == "config":
                await ConfigHelpMenu(ctx).start()
            else:
                await ctx.respond(
                    embed=self.bot.embed.build(
                        ctx=ctx,
                        header="Help",
                        description=f"{lightbulb.get_help_text(self.bot.get_command(f'{cmd.name}'))}",
                        thumbnail=self.bot.get_me().avatar_url,
                        fields=(
                            ("Syntax (<required> • [optional])", self.full_syntax(ctx, cmd, prefix), False),
                            (
                                "On cooldown?",
                                f"Yes, for {chron.long_delta(dt.timedelta(seconds=s))}."
                                if (s := cmd.cooldown_manager)
                                else "No",
                                False,
                            ),
                            ("Can be run?", cmd.user_required_permissions, False),
                            (
                                "Parent",
                                self.full_syntax(ctx, p, prefix) if (p := cmd.parent) is not None else "None",
                                False,
                            ),
                        ),
                    )
                )

        else:
            pagemaps = []

            for extension, cmds in (await self.get_command_mapping(ctx)).items():
                pagemaps.append(
                    {
                        "header": "Help",
                        "title": f"The `{self.bot.get_plugin(extension.title()).name}` module",
                        "description": f"{self.bot.get_plugin(extension.title()).__doc__}\n\nUse `{prefix}help [command]` for more detailed help on a command. You can not run commands with `(✗)` next to them.",
                        "thumbnail": self.bot.get_me().avatar_url,
                        "fields": (
                            (
                                f"{len(cmds)} command(s)",
                                "```{}```".format(
                                    "\n".join([await self.basic_syntax(ctx, cmd, prefix) for cmd in cmds])
                                ),
                                False,
                            ),
                        ),
                    }
                )

            await HelpMenu(ctx, pagemaps).start()


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Help(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Help")
