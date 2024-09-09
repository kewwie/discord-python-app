import discord
from discord import app_commands
from discord.ext import commands

class Profile(commands.Cog, name="profile"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.hybrid_command(
        name="profile",
        description="Get the profile of a member or yourself",
        aliases=["account"]
    )
    @app_commands.describe(
        member="The member to get the profile of",
    )
    async def rank(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author

        levelUser = self.client.database.levels.find_one({"user_id": member.id})

        if not levelUser:
            await ctx.reply("This user has no xp")
            return

        level = levelUser["level"]
        xp = levelUser["xp"]
        neededXp = await self.client.calculateLevelXp(level + 1) - await self.client.calculateLevelXp(level)
        levelXp = xp - await self.client.calculateLevelXp(level)

        profileDescription = f"**Rank:** Soon\n"
        profileDescription += f"**Level:** {level}\n"
        profileDescription += f"**Progress:** ${levelXp} / ${neededXp}\n"

        embed = discord.Embed(
            title=f"{member.username}'s profile",
            color=discord.Color("#2b2d31"),
            description=profileDescription
        )

async def setup(client) -> None:
    await client.add_cog(Profile(client))