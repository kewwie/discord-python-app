import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class Utils(commands.Cog, name="utils"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(
        name="reload-commands",
        description="Reload all the commands",
        hidden=True
    )
    @commands.is_owner()
    async def reload_commands(self, ctx: commands.Context) -> None:
        await self.client.tree.sync()

        response = await ctx.reply("Reloaded all commands")
        await asyncio.sleep(5)
        await ctx.message.delete()
        await response.delete()

    @commands.hybrid_command(
        name="members",
        description="Get the current member count of the server",
        aliases=["member-count", "membercount"]
    )
    async def members(self, ctx: commands.Context) -> None:
        await ctx.reply(f"This server has {format(ctx.guild.member_count, ",")} members")

    @commands.command(
        name="ping",
        description="Get the current bot latency",
        aliases=["pong"]
    )
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.reply(f"Pong! {round(self.client.latency * 1000)}ms")

    @commands.hybrid_command(
        name="avatar",
        description="Get the avatar of a user or yourself",
        aliases=["av"]
    )
    @app_commands.describe(
        member="The user to get the avatar of",
    )
    async def avatar(self, ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        await ctx.reply(member.avatar)
    
    @commands.hybrid_command(
        name="join-date",
        description="Get the join date of a member or yourself",
        aliases=["joindate", "joined-at", "joined"]
    )
    @app_commands.describe(
        member="The user to get the join date of",
    )
    async def join_date(self, ctx: commands.Context, member: discord.Member = None) -> None:
        member = member or ctx.author
        await ctx.reply(f"{member.mention} joined on **{member.joined_at.strftime('%d %B %Y')}** at **{member.joined_at.strftime('%H:%M:%S')}**")
        

async def setup(client) -> None:
    await client.add_cog(Utils(client))