import hikari
import lightbulb
from hikari import events

from bluebrain import Config
from bluebrain.bot import Blue_Bot

class Hub(lightbulb.Plugin):
    def __init__(self, bot: Blue_Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.plugins.listener()
    async def on_started(self, event: hikari.StartedEvent) -> None:
        if not self.bot.ready.booted:
            self.bot.ready.up(self)
            
        self.guild = await self.bot.rest.fetch_guild(Config.HUB_GUILD_ID)

        if self.guild is not None:
            self.commands_channel = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
            self.relay_channel = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
            self.stdout_channel = self.guild.get_channel(Config.HUB_STDOUT_CHANNEL_ID)

            if self.stdout_channel is not None:
                await self.stdout_channel.send(
                    f"{(await self.bot.info)} Blue Brain is now online! (Version {self.bot.version})"
                )


    @lightbulb.plugins.listener()
    async def on_guild_join(self, event: events.GuildJoinEvent) -> None:
        self.guild = await self.bot.rest.fetch_guild(Config.HUB_GUILD_ID)

        if self.guild is not None:
            self.stdout_channel = self.guild.get_channel(Config.HUB_STDOUT_CHANNEL_ID)

        guild_name = str(event.guild)

        await self.bot.db.execute("INSERT OR IGNORE INTO system (GuildName, GuildID) VALUES (?, ?)", guild_name, event.guild_id,)
        await self.bot.db.execute("INSERT OR IGNORE INTO gateway (GuildID) VALUES (?)", event.guild_id,)
        await self.bot.db.execute("INSERT OR IGNORE INTO warn (GuildID) VALUES (?)", event.guild_id,)

        if self.stdout_channel is not None:
            await self.stdout_channel.send(
                f"{(await self.bot.info)} Joined guild! Nº: `{self.bot.guild_count}` • Name: `{event.guild}` • Members: `{len(event.members):,}` • ID: `{event.guild.id}`"
            )


    @lightbulb.plugins.listener()
    async def on_guild_leave(self, event: events.GuildLeaveEvent) -> None:
        self.guild = await self.bot.rest.fetch_guild(Config.HUB_GUILD_ID)

        if self.guild is not None:
            self.stdout_channel = self.guild.get_channel(Config.HUB_STDOUT_CHANNEL_ID)

        guild_name = await self.bot.db.record("SELECT GuildName FROM system WHERE GuildID = ?", event.guild_id)

        await self.bot.db.execute("DELETE FROM system WHERE GuildID = ?", event.guild_id)
        await self.bot.db.execute("DELETE FROM gateway WHERE GuildID = ?", event.guild_id)
        await self.bot.db.execute("DELETE FROM warn WHERE GuildID = ?", event.guild_id)

        if self.stdout_channel is not None:
            await self.stdout_channel.send(
                f"{(await self.bot.info)} Left guild. Name: `{guild_name[0]}` • Members: `Null` • ID: `{event.guild_id}` • Nº of guild now: `{self.bot.guild_count}`"
            )


    @lightbulb.plugins.listener()
    async def on_guild_message_create(self, event: events.GuildMessageCreateEvent) -> None:
        self.guild = await self.bot.rest.fetch_guild(Config.HUB_GUILD_ID)

        if self.guild is not None:
            self.commands_channel = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
            self.relay_channel = self.guild.get_channel(Config.HUB_COMMANDS_CHANNEL_ID)
            self.stdout_channel = self.guild.get_channel(Config.HUB_STDOUT_CHANNEL_ID)

        server = await self.bot.rest.fetch_guild(event.guild_id)
        channel = server.get_channel(event.channel_id)

        if event.is_bot or not event.content:
            return
        
        if server == self.guild and not event.is_bot and event.author_id == 714022418200657971:
            if channel == self.commands_channel:
                if event.content.startswith("shutdown") or event.content.startswith("sd"):
                    await self.bot.close()

            elif channel == self.relay_channel:
                # TODO: Add relay system.
                pass



def load(bot: Blue_Bot) -> None:
    bot.add_plugin(Hub(bot))

def unload(bot: Blue_Bot) -> None:
    bot.remove_plugin("Hub")