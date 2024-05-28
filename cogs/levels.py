import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random

from easy_pil import Canvas, Editor, Font, load_image

class Levels(commands.Cog, name="levels"):
    def __init__(self, client) -> None:
        self.client = client

    @commands.hybrid_command(
        name="rank",
        description="Get the level of a member",
        aliases=["level", "lvl"]
    )
    @app_commands.describe(
        member="The member to get the rank of",
    )
    async def rank(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author

        levelUser = self.client.database.levels.find_one({"user_id": member.id})

        level = levelUser["level"]
        xp = levelUser["xp"]
        neededXp = await self.client.functions.calculateLevelXp(level + 1) - await self.client.functions.calculateLevelXp(level)
        levelXp = xp - await self.client.functions.calculateLevelXp(level)

        user_data = {
            "name": member.name,
            "xp": levelXp,
            "next_level_xp": neededXp,
            "level": level,
            "percentage": (levelXp / neededXp) * 100,
        }

        background = Editor(Canvas((900, 300), color="#23272A"))
        profile_image = load_image(str(member.avatar))
        profile = Editor(profile_image).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        card_right_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]

        background.polygon(card_right_shape, "#2C2F33")
        background.paste(profile, (30, 30))

        background.rectangle((30, 220), width=650, height=40, fill="#494b4f", radius=20)
        background.bar(
            (30, 220),
            max_width=650,
            height=40,
            percentage=user_data["percentage"],
            fill="#3db374",
            radius=20,
        )
        background.text((200, 40), user_data["name"], font=poppins, color="white")

        background.rectangle((200, 100), width=350, height=2, fill="#17F3F6")
        background.text(
            (200, 130),
            f"Level : {user_data['level']} "
            + f" XP : {user_data['xp']} / {user_data['next_level_xp']}",
            font=poppins_small,
            color="white",
        )

        file = discord.File(fp=background.image_bytes, filename="card.png")

        await ctx.send(file=file)

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

        boosts = sorted(self.client.config["xpBoosts"], key=lambda x: x["multiplier"], reverse=True)
        for role in message.author.roles:
            for boost in boosts:
                if boost["role_id"] == role.id:
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