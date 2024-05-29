import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random

class Fun(commands.Cog, name="fun"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(
        name="self-timeout",
        description="Put yourself in timeout",
        aliases=["selftimeout"]
    )
    @commands.bot_has_permissions(moderate_members=True)
    async def self_timeout(self, ctx: commands.Context) -> None:
        timeout_time = datetime.datetime.now() + datetime.timedelta(seconds=30)
        timeout_time = discord.utils.utcnow() + datetime.timedelta(seconds=30)
        try:
            await ctx.author.timeout(timeout_time)
        except Exception:
            return
        
    @commands.hybrid_command(
        name="8ball",
        description="Ask the magic 8ball a question",
        aliases=["eightball"]
    )
    @app_commands.describe(
        question="The question to ask the 8ball"
    )
    async def eight_ball(self, ctx: commands.Context, question: str) -> None:
        responses = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes, definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ]
        await ctx.reply(f"Question: {question}\nAnswer: {random.choice(responses)}")

    

async def setup(client) -> None:
    await client.add_cog(Fun(client))