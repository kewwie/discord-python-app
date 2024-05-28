import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random

class Levels(commands.Cog, name="levels"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.command(name="rank", description="Get the rank of a member", aliases=["level", "lvl"])
    async def rank(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author

        levelUser = self.client.database.levels.find_one({"user_id": member.id})

        level = levelUser["level"]
        xp = levelUser["xp"]
        neededXp = await self.client.functions.calculateLevelXp(level + 1) - xp
        levelXp = xp - await self.client.functions.calculateLevelXp(level)

        await ctx.reply(f"**{member.name}**\nLevel {level}\n{levelXp}/{neededXp} Xp")

    @app_commands.command(name="rank", description="Get the rank of a member")
    @app_commands.describe(
        member="The member to get the rank of",
    )
    async def slashRank(self, interaction: discord.Integration, member: discord.Member = None) -> None:
        if not member: member = interaction.user

        levelUser = self.client.database.levels.find_one({"user_id": member.id})
        
        level = levelUser["level"]
        xp = levelUser["xp"]
        neededXp = await self.client.functions.calculateLevelXp(level + 1) - xp
        levelXp = xp - await self.client.functions.calculateLevelXp(level)


        await interaction.response.send_message(f"**{member.name}**\nLevel {level}\n{levelXp}/{neededXp} Xp")

    @commands.hybrid_command(
        name="leaderboard",
        with_app_command=True,
        description="Get the rank of a member",
        aliases=["lb", "levels"]
    )
    async def leaderboard(self, ctx: commands.Context) -> None:
        await ctx.reply("Leaderboard Will Be Added Later", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.client.user or message.author.bot:
            return
        
        newXp = random.randint(45, 55)

        for boost in sorted(self.client.config["xpBoosts"], key=lambda x: x["multiplier"], reverse=True):
            if boost["role_id"] in [role.id for role in message.author.roles]:
                newXp *= boost["multiplier"]
                break

        levelUser = self.client.database.levels.find_one({"user_id": message.author.id})
        if levelUser:
            if levelUser["last_updated"] > datetime.datetime.now() - datetime.timedelta(minutes=1):
                return
            
            level = levelUser["level"]
            xp = levelUser["xp"] + newXp
            neededXp = await self.client.functions.calculateLevelXp(level + 1) - xp

            if (neededXp <= 0):
                level = levelUser["level"] + 1

                await message.channel.send(f"Congrats, you have reached level {level}!")

                reward = next((reward for reward in self.client.config["levelRewards"] if reward["level"] == level), None)
                if reward:
                    role = message.guild.get_role(reward["role_id"])
                    if role:
                        await message.author.add_roles(role)
                

            self.client.database.levels.update_one(
                {
                    "user_id": message.author.id,
                    "guild_id": message.guild.id
                },
                {
                    "$set": {
                        "xp": xp,
                        "level": level,
                        "last_updated": datetime.datetime.now()
                    }
                }
            )
        else:
            neededXp = await self.client.functions.calculateLevelXp(1)
            self.client.database.levels.insert_one({
                "user_id": message.author.id,
                "guild_id": message.guild.id,
                "xp": newXp,
                "level": 0,
                "last_updated": datetime.datetime.now()
            })

async def setup(client) -> None:
    await client.add_cog(Levels(client))