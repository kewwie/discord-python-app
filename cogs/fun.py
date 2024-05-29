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
        aliases=["selftimeout", "self-time", "selftime"]
    )
    @commands.bot_has_permissions(moderate_members=True)
    async def self_timeout(self, ctx: commands.Context) -> None:
        timeout_time = discord.utils.utcnow() + datetime.timedelta(seconds=30)
        try:
            await ctx.author.timeout(timeout_time, "Self timeout")
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
            "Yes",
            "No",
            "Maybe",
            "Never",
            "Definitely",
            "Always"
        ]
        await ctx.reply(f"{random.choice(responses)}")

async def setup(client) -> None:
    await client.add_cog(Fun(client))