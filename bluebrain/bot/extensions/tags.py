import hikari
import lightbulb

import typing as t
from string import ascii_lowercase

from bluebrain.bot import Blue_Bot
from bluebrain.utils import menu, checks, markdown, converters

#MAX_TAGS = 35
MAX_TAGNAME_LENGTH = 25

class HelpMenu(menu.MultiPageMenu):
    def __init__(self, ctx, pagemaps):
        super().__init__(ctx, pagemaps, timeout=120.0)

class Tags(lightbulb.Plugin):
    """Commands for creating tags."""
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
    @lightbulb.command(name="tag")
    async def tag_command(self, ctx: lightbulb.Context, tag_name: str) -> None:
        """Shows the content of an existing tag."""
        if any(c not in ascii_lowercase for c in tag_name):
            return await ctx.respond(f"{(await self.bot.cross)} Tag identifiers can only contain lower case letters.")

        tag_names= await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)

        cache = []

        if tag_name not in tag_names:
            await ctx.respond(f'{(await self.bot.cross)} The Tag `{tag_name}` does not exist.')
            for x in range(len(tag_names)):
                if tag_names[x][0] == tag_name[0]:
                    cache.append(tag_names[x])
                    return await ctx.respond("Did you mean..." + '\n'.join(cache) + " ?")

        else:
        	content, tag_id = await self.bot.db.record("SELECT TagContent, TagID FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)

        	await ctx.respond(content)


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.group(
        name="tags",
        insensitive_commands=True,
        inherit_checks=True
    )
    async def tags_group(self, ctx: lightbulb.Context) -> None:
        """Commands to create tags in the server."""
        prefix = await self.bot.prefix(ctx.get_guild().id)
        cmds = sorted(ctx.command.subcommands, key=lambda c: c.name)

        await ctx.respond(
            embed=self.bot.embed.build(
                ctx=ctx,
                header="Tags",
                thumbnail=self.bot.get_me().avatar_url,
                description="There are a few different tag methods you can use.",
                fields=(
                    *(
                        (
                            cmd.name.title(),
                            #f"{lightbulb.get_help_text(self.bot.get_command(cmd.name))} For more infomation, use `{prefix}help tags {cmd.name}`",
                            f"{lightbulb.get_help_text(self.bot.get_command(f'{ctx.command.name} {cmd.name}'))} For more infomation, use `{prefix}help tags {cmd.name}`",
                            False,
                        )
                        for cmd in cmds
                    ),
                ),
            )
        )


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(name = "new")
    async def tag_create(self, ctx: lightbulb.Context, tag_name: str, *, content) -> None:
        """Creates a new tag."""
        if any(c not in ascii_lowercase for c in tag_name):
            return await ctx.respond(f"{(await self.bot.cross)} Tag identifiers can only contain lower case letters.")

        if len(tag_name) > MAX_TAGNAME_LENGTH:
            return await ctx.respond(
                f"{(await self.bot.cross)} Tag identifiers must not exceed `{MAX_TAGNAME_LENGTH}` characters in length."
            )

        tag_names = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)

        #if len(tag_names) == MAX_TAGS:
            #return await ctx.send(f"{self.bot.cross} You can only set up to {MAX_TAGS} warn types.")

        if tag_name in tag_names:
            prefix = await self.bot.prefix(ctx.guild)
            return await ctx.repond(
                f"{(await self.bot.cross)} That tag already exists. You can use `{prefix}tag edit {tag_name}`"
            )

        await self.bot.db.execute(
            "INSERT INTO tags (GuildID, UserID, TagID, TagName, TagContent) VALUES (?, ?, ?, ?, ?)",
            ctx.get_guild().id,
            ctx.author.id,
            self.bot.generate_id(),
            tag_name,
            content
        )
        await ctx.respond(f'{(await self.bot.tick)} The tag `{tag_name}` has been created.')


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(
        name="edit"
    )
    async def tag_edit(self, ctx: lightbulb.Context, tag_name: str, *, content):
        """Edits an existing tag."""
        if any(c not in ascii_lowercase for c in tag_name):
            return await ctx.repond(f"{(await self.bot.cross)} Tag identifiers can only contain lower case letters.")

        user_id, tag_id = await self.bot.db.record("SELECT UserID, TagID FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)

        if user_id != ctx.author.id:
            return await ctx.repond(f"{(await self.bot.cross)} You can't edit others tags. You can only edit your own tags.")

        else:
            tag_content = await self.bot.db.column("SELECT TagContent FROM tags WHERE GuildID = ?", ctx.get_guild().id)
            tag_names = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)

            if tag_name not in tag_names:
                return await ctx.repond(f'{(await self.bot.cross)} The tag `{tag_name}` does not exist.')

            if content in tag_content:
                return await ctx.repond(f'{(await self.bot.cross)} That content already exists in this `{tag_name}` tag.')

            await self.bot.db.execute(
                "UPDATE tags SET TagContent = ? WHERE GuildID = ? AND TagName = ?",
                content,
                ctx.get_guild().id,
                tag_name,
            )

            await ctx.respond(
                f"{(await self.bot.tick)} The `{tag_name}` tag's content has been updated."
            )


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(
        name="delete",
        aliases=["del"]
    )
    async def tag_delete_command(self, ctx: lightbulb.Context, tag_name: str) -> None:
        """Deletes an existing tag."""
        if any(c not in ascii_lowercase for c in tag_name):
            return await ctx.respond(f"{(await self.bot.cross)} Tag identifiers can only contain lower case letters.")

        user_id, tag_id = await self.bot.db.record("SELECT UserID, TagID FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)

        if user_id != ctx.author.id:
            return await ctx.respond(f"{(await self.bot.cross)} You can't delete others tags. You can only delete your own tags.")

        modified = await self.bot.db.execute(
            "DELETE FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name
        )

        if not modified:
            return await ctx.respond(f"{(await self.bot.cross)} That tag does not exist.")

        await ctx.send(f'{self.bot.tick} Tag `{tag_name}` deleted.')


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(name = "info")
    async def tag_info_command(self, ctx: lightbulb.Context, tag_name: str) -> None:
        """Shows information about an existing tag."""
        if any(c not in ascii_lowercase for c in tag_name):
            return await ctx.respond(f"{(await self.bot.cross)} Tag identifiers can only contain lower case letters.")

        tag_names = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)

        if tag_name not in tag_names:
            return await ctx.respond(f'{(await self.bot.cross)} The Tag `{tag_name}` does not exist.')

        user_id, tag_id, tag_time = await self.bot.db.record("SELECT UserID, TagID, TagTime FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)

        user = await self.bot.rest.fetch_user(user_id)

        embed = hikari.Embed(title = 'Tag Info', colour = ctx.member.get_top_role().color, timestamp = ctx.message.created_at)
        embed.set_thumbnail(user.avatar_url)
        embed.add_field(name = "Owner", value = user.mention, inline = False)
        embed.add_field(name = "Tag Name", value = tag_name, inline = True)
        embed.add_field(name = "Tag ID", value = tag_id, inline = True)
        embed.add_field(name = "Created at", value = tag_time, inline = True)
        embed.set_footer(text = f"Requested by {ctx.author.username}", icon = ctx.author.avatar_url)

        await ctx.respond(embed = embed)


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(name = "all")
    async def member_tag_list_command(self, ctx: lightbulb.Context, target: t.Optional[converters.SearchedMember]) -> None:
        """Shows the tag list of a tag owner."""
        target = target or ctx.author
        prefix = await self.bot.prefix(ctx.get_guild().id)
        all_tags = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)
        tag_names = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ? AND UserID = ?", ctx.get_guild().id, target.id)
        tag_all = await self.bot.db.records("SELECT Tagname, TagID FROM tags WHERE GuildID = ? AND UserID = ?", ctx.get_guild().id, target.id)
        if len(tag_names) == 0:
            if target == ctx.author:
                return await ctx.respond(f"{(await self.bot.cross)} You don't have any tag list.")
            else:
                return await ctx.respond(f"{(await self.bot.cross)} That member doesn't have any tag list.")

        self.user = await self.bot.grab_user(target.id)

        try:
            pagemaps = []

            for tag_name, tag_id in sorted(tag_all):
                content, tag_id = await self.bot.db.record("SELECT TagContent, TagID FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)
                first_step = content
                pagemaps.append(
                    {
                        "header": "Tags",
                        "title": f"All tags of this server for {self.user.username}",
                        "description": f"Using {len(tag_names)} of this server's {len(all_tags)} tags.",
                        "thumbnail":self.user.avatar_url,
                        "fields": (
                            (
                                tag_name,
                                "ID: " + tag_id + "\n\n**Content**" + "\n```\n" + ''.join(first_step.replace('<', '\\<')[0:350]) + "..." + "\n\n```\n***To see this tags whole content type `" + prefix + "tag " + tag_name + "`***",
                                False
                                ),
                            ),
                        }
                    )

            await HelpMenu(ctx, pagemaps).start()

        except IndexError:
            await ctx.send(
                embed=self.bot.embed.build(
                ctx=ctx,
                header="Tags",
                title=f"All tags of this server for {self.user.username}",
                description=f"Using {len(tag_names)} of this server's {len(all_tags)} tags.",
                thumbnail=self.user.avatar_url,
                fields=((tag_name, f"ID: {tag_id}", True) for tag_name, tag_id in sorted(tag_all)),
            )
        )


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(name = "raw")
    async def raw_command(self, ctx: lightbulb.Context, tag_name: str) -> None:
        """Gets the raw content of the tag. This is with markdown escaped. Useful for editing."""
        if any(c not in ascii_lowercase for c in tag_name):
            return await ctx.respond(f"{(await self.bot.cross)} Tag identifiers can only contain lower case letters.")

        tag_content = await self.bot.db.column("SELECT TagContent FROM tags WHERE GuildID = ?", ctx.get_guild().id)
        tag_names = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)

        if tag_name not in tag_names:
            return await ctx.respond(f'{(await self.bot.cross)} The Tag `{tag_name}` does not exist.')

        content, tag_id = await self.bot.db.record("SELECT TagContent, TagID FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)

        first_step = markdown.escape_markdown(content)
        await ctx.respond(first_step.replace('<', '\\<'))


    @checks.bot_has_booted()
    @checks.bot_is_ready()
    @lightbulb.check(lightbulb.guild_only)
    @tags_group.command(
        name="list"
    )
    async def tags_list_command(self, ctx: lightbulb.Context) -> None:
        """Lists the server's tags."""
        prefix = await self.bot.prefix(ctx.get_guild().id)
        tag_names = await self.bot.db.column("SELECT TagName FROM tags WHERE GuildID = ?", ctx.get_guild().id)
        records = await self.bot.db.records("SELECT TagName, TagID FROM tags WHERE GuildID = ?", ctx.get_guild().id)

        try:
            pagemaps = []

            for tag_name, tag_id in sorted(records):
                content, tag_id = await self.bot.db.record("SELECT TagContent, TagID FROM tags WHERE GuildID = ? AND TagName = ?", ctx.get_guild().id, tag_name)
                first_step = content
                pagemaps.append(
                    {
                        "header": "Tags",
                        "title": f"All tags of this server",
                        "description": f"A total of {len(tag_names)} tags of this server.",
                        "thumbnail": ctx.get_guild().icon_url,
                        "fields": (
                            (
                                tag_name,
                                "ID: " + tag_id + "\n\n**Content**" + "\n```\n" + ''.join(first_step.replace('<', '\\<')[0:350]) + "..." + "\n\n```\n***To see this tags whole content type `" + prefix + "tag " + tag_name + "`***",
                                False
                                ),
                            ),
                        }
                    )

            await HelpMenu(ctx, pagemaps).start()

        except IndexError:
            await ctx.send(
                embed=self.bot.embed.build(
                ctx=ctx,
                header="Tags",
                title="All tags of this server",
                description=f"A total of {len(tag_names)} tags of this server.",
                thumbnail=ctx.get_guild().icon_url,
                fields=((tag_name, f"ID: {tag_id}", True) for tag_name, tag_id in sorted(records)),
            )
        )


def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Tags(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Tags")
