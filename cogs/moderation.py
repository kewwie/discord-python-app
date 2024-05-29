import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog, name="moderation"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(
        name="timeout",
        description="Put a user in timeout",
        aliases=["mute", "time", "t"]
    )
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(manage_messages=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, time: str, *, reason: str = "No reason provided") -> None:
        if time.endswith("s"):
            timeout_time = datetime.timedelta(seconds=int(time[:-1]))
        elif time.endswith("m"):
            timeout_time = datetime.timedelta(minutes=int(time[:-1]))
        elif time.endswith("h"):
            timeout_time = datetime.timedelta(hours=int(time[:-1]))
        elif time.endswith("d"):
            timeout_time = datetime.timedelta(days=int(time[:-1]))
        else:
            await ctx.reply("Invalid time format")
            return
        
        if timeout_time.days > 27:
            timeout_time = datetime.timedelta(days=27)
        
        await member.timeout(discord.utils.utcnow() + timeout_time)

async def setup(client) -> None:
    await client.add_cog(Moderation(client))