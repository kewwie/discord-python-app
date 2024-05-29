import discord
from discord.ext import commands
import json
import os

import pymongo

from dotenv import load_dotenv
load_dotenv()

def config():
    with open("config.json") as file:
        return json.load(file)

intents = discord.Intents.all()

class Fuctions():
    def __init__(self, client):
        self.client = client
    
    async def calculateLevelXp(self, level: int) -> int:
        xp = (400 * level) + ((level * 250) * level)
        return xp


class CustomApp(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = commands.when_mentioned_or(config()["prefix"]),
            owner_ids = config()["owners"],
            intents = intents,
            status=discord.Status.online,
            activity = discord.CustomActivity(name=config()["activity"]),
            help_command=None
        )
        self.database = (pymongo.MongoClient(os.getenv("MONGO_URI"))).database
        self.functions = Fuctions(self)
        self.config = config()

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

    async def on_command_error(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            return
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply("I don't have the required permissions to run this command", ephemeral=True)

        elif isinstance(error, commands.NotOwner):
            await ctx.message.delete()
            return
    
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply("You don't have the required permissions to run this command", ephemeral=True)
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"Command is on cooldown. Try again in {round(error.retry_after, 2)}s", ephemeral=True)
        
        else:
            return

client = CustomApp()
client.run(os.getenv("TOKEN"))