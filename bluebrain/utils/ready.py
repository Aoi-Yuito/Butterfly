class Ready:
    def __init__(self, bot):
        self.bot = bot
        self.booted = False
        self.synced = False

        for extension in self.bot._extensions:
            setattr(self, extension, False)

    def up(self, extension):
        setattr(self, qn := extension.name.lower(), True)
        print(f"   • `{qn}` extension ready.")

    @property
    def ok(self):
        return self.booted and all(getattr(self, extension) for extension in self.bot._extensions)

    @property
    def initialised_extensions(self):
        return [extension for extension in self.bot._extensions if getattr(self, extension)]

    def __str__(self):
        string = "Bot is booted." if self.booted else "Bot is not booted."
        string += f" {len(self.initialised_extensions)} of {len(self.bot._extensions)} extensions initialised."
        return string

    def __repr__(self):
        return f"<Ready booted={self.booted!r} ok={self.ok!r}>"

    def __int__(self):
        return len(self.initialised_extensions)

    def __bool__(self):
        return self.ok