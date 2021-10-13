from hikari import Embed

from datetime import datetime

from bluebrain.utils import DEFAULT_EMBED_COLOUR


class EmbedConstructor:
    def __init__(self, bot):
        self.bot = bot

    def build(self, **kwargs):
        ctx = kwargs.get("ctx")

        embed = Embed(
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            colour=(
                kwargs.get("colour")
                or (ctx.member.get_top_role().color if ctx and ctx.member.get_top_role().color else None)
                or DEFAULT_EMBED_COLOUR
            ),
            timestamp=datetime.now().astimezone(),
        )

        embed.set_author(name=kwargs.get("header", "Blue Brain"))
        embed.set_footer(
            text=kwargs.get("footer", f"Invoked by {ctx.author.username}" if ctx else r"\o/"),
            icon=ctx.author.avatar_url if ctx else self.bot.get_me().avatar_url,
        )

        if thumbnail := kwargs.get("thumbnail"):
            embed.set_thumbnail(thumbnail)

        if image := kwargs.get("image"):
            embed.set_image(image)

        for name, value, inline in kwargs.get("fields", ()):
            embed.add_field(name=name, value=value, inline=inline)

        return embed