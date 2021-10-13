from collections import deque

from apscheduler.triggers.cron import CronTrigger
from hikari import Status, Activity, ActivityType

ACTIVITY_TYPES = (ActivityType.WATCHING, ActivityType.PLAYING, ActivityType.LISTENING, ActivityType.STREAMING)


class PresenceSetter:
    def __init__(self, bot):
        self.bot = bot

        self._name = "@Blue Brain help • {message} • Version {version}"
        self._type = "watching"
        self._messages = deque(
            (
                "Invite Blue Brain to your server by using @Blue Brain invite",
                "To view information about Blue Brain, use @Solaris botinfo",
                "Need help with Blue Brain? Join the support server! Use @Blue Brain support to get an invite",
                "Developed by Yuito | 碧 唯翔#8637, and available under the GPLv3 license",
            )
        )

        self.bot.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def name(self):
        message = self._messages[0].format(bot=self.bot)
        return self._name.format(message=message, version=self.bot.version)

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self):
        return getattr(ActivityType, self._type, ActivityType.WATCHING)

    @type.setter
    def type(self, value):
        if value not in ACTIVITY_TYPES:
            raise ValueError("The activity should be one of the following: {}".format(", ".join(ACTIVITY_TYPES)))

        self._type = value

    async def set(self):
        await self.bot.update_presence(status=Status.ONLINE, activity=Activity(name=self.name, type=self.type))
        self._messages.rotate(-1)