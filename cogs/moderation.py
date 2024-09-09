import discord
from discord.ext import commands
import datetime

import json
def config():
    with open("config.json") as file:
        return json.load(file)


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, client) -> None:
        self.client = client

    def is_staff():
        def predicate(ctx):
            roles = [role.id for role in ctx.author.roles]
            for perms in config()["permissions"]:
                if perms["staff"] is True and perms[ctx.command.name] is True:
                    if perms["id"] in roles:
                        return True
            raise commands.MissingRole()
        return commands.check(predicate)

    @commands.command(
        name="timeout",
        description="Put a user in timeout",
        aliases=["mute", "time", "t"]
    )
    @commands.bot_has_permissions(moderate_members=True)
    @is_staff()
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

        self.client.database.infractions.insert_one({
            "guild_id": ctx.message.guild.id,
            "user_id": ctx.message.author.id,
            "user_name": ctx.message.author.name,
            "reason": reason,
            "created_at": datetime.datetime.now()
        })

    @commands.command(
        name="ban",
        description="Ban a user from the server"
    )
    @commands.bot_has_permissions(ban_members=True)
    @is_staff()
    async def ban(self, ctx: commands.Context, user: discord.User, *, reason: str = "No reason provided") -> None:
        await ctx.message.delete()

        ban_entry = await ctx.guild.fetch_ban(user)
        if ban_entry:
            await ctx.send(f"<@{ctx.author.id}> **{user.name}** is already banned", delete_after=3)
        else:
            await ctx.guild.ban(user=user, delete_message_days=1, reason=reason)
            await ctx.send(f"<@{ctx.author.id}> **{user.name}** has been banned", delete_after=3)

    @commands.command(
        name="unban",
        description="Unban a user from the server"
    )
    @commands.bot_has_permissions(ban_members=True)
    @is_staff()
    async def unban(self, ctx: commands.Context, user: discord.User) -> None:
        await ctx.message.delete()
        await ctx.guild.unban(user.id)
        await ctx.send(f"<@{ctx.author.id}> **{user.name}** has been unbanned", delete_after=3)

async def setup(client) -> None:
    await client.add_cog(Moderation(client))