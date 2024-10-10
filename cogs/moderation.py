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
                    if perms["roleid"] in roles:
                        return True
            raise commands.CheckFailure("You don't have the required permissions to run this command")
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
        elif time.isdigit():
            time = datetime.timedelta(minutes=int(time))
        else:
            await ctx.reply("Invalid time format")
            return
        
        if time and time.days > 27:
            await ctx.reply("You can't timeout for more than 27 days")
            return
        
        embed = discord.Embed(
            title="User Timed Out",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Duration", value=f"{int(time.total_seconds() // 60)} minutes", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Moderator: {ctx.author.name}")

        if time:
            time = discord.utils.utcnow() + time
            self.client.database.infractions.insert_one({
                "guild_id": ctx.message.guild.id,
                "user_id": member.id,
                "user_name": member.name,
                "mod_id": ctx.message.author.id,
                "mod_name": ctx.message.author.name,
                "reason": reason,
                "created_at": datetime.datetime.now()
            })

        await member.timeout(time, reason=reason)
        await ctx.message.delete()

        await ctx.send(embed=embed)

    @commands.command(
        name="infractions",
        description="Get the infractions of a user",
        aliases=["infraction", "infs"]
    )
    @commands.bot_has_permissions(send_messages=True)
    async def infractions(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author
  
        infractions = self.client.database.infractions.find({
            "guild_id": ctx.guild.id,
            "user_id": member.id
        })

        if self.client.database.infractions.count_documents({
            "guild_id": ctx.guild.id,
            "user_id": member.id
        }) == 0:
            await ctx.send(f"**{member.name}** has no infractions")
            return

        embed = discord.Embed(
            title=f"Infractions for {member.name}",
            color=discord.Color.red()
        )

        infraction_number = 0
        for infraction in infractions:
            infraction_number += 1
            expires_in = (infraction["created_at"] + datetime.timedelta(days=60)) - datetime.datetime.now()
            embed.add_field(
                name=f"Infraction {infraction_number} (Expires In {expires_in.days} days)",
                value=f"**Reason:** {infraction['reason']}",
                inline=False
            )

        await ctx.send(embed=embed)

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