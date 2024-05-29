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
            time = datetime.timedelta(seconds=int(time[:-1]))
        elif time.endswith("m"):
            time = datetime.timedelta(minutes=int(time[:-1]))
        elif time.endswith("h"):
            time = datetime.timedelta(hours=int(time[:-1]))
        elif time.endswith("d"):
            time = datetime.timedelta(days=int(time[:-1]))
        elif time == "0":
            time = None
        else:
            await ctx.reply("Invalid time format")
            return
        
        if time and time.days > 27:
            await ctx.reply("You can't timeout for more than 27 days")
            return

        if time:
            time = discord.utils.utcnow() + time
        
        await member.timeout(time, reason=reason)
        await ctx.message.delete()

async def setup(client) -> None:
    await client.add_cog(Moderation(client))