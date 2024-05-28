import discord
from discord import app_commands
from discord.ext import commands

class Levels(commands.Cog, name="levels"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command("rank")
    async def rank(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author

        await ctx.reply(member.mention)

    @app_commands.command(name="rank", description="Get the rank of a member")
    @app_commands.describe(
        member="The member to get the rank of",
    )
    async def slashRank(self, interaction: discord.Integration, member: discord.Member = None) -> None:
        if not member: member = interaction.user

        await interaction.response.send_message(member.name, ephemeral=True)

    @commands.hybrid_command(name="leaderboard", with_app_command=True, description="Get the rank of a member")
    async def leaderboard(self, ctx: commands.Context) -> None:
        await ctx.reply("Leaderboard", ephemeral=True)

async def setup(client) -> None:
    await client.add_cog(Levels(client))