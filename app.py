import discord
from discord.ext import commands
import os

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.all()

class DisPy(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned_or("!"),
            owner_ids = [292948682884775937],
            intents = intents,
            status=discord.Status.online,
            activity = discord.CustomActivity(name="Kewi is the best!"),
        )

    async def load_cogs(self) -> None:
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)
    
    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")
        await self.load_cogs()
        await self.tree.sync()

    async def on_command_error(self, ctx: commands.Context, error) -> None:
        await ctx.reply(error, ephemeral=True)

client = DisPy()
client.run(os.getenv("TOKEN"))