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
        name="xp",
        description="Get your current or someone else's xp",
        aliases=["get-xp"]
    )
    @app_commands.describe(
        member="The member to get the xp of",
    )
    async def xp(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author

        levelUser = self.client.database.levels.find_one({"user_id": member.id})

        if not levelUser:
            await ctx.reply("This user has no xp")
            return

        await ctx.send(f"{member.mention}: {format(levelUser['xp'], ',')} Xp")

    @commands.command(
        name="text-rank",
        description="Get the level of a member or yourself",
        aliases=["trank", "text-level", "tlevel"],
        hidden=True
    )
    async def text_rank(self, ctx: commands.Context, member: discord.Member = None) -> None:
        if not member: member = ctx.author

        levelUser = self.client.database.levels.find_one({"user_id": member.id})

        if not levelUser:
            await ctx.reply("This user has no xp")
            return

        level = levelUser["level"]
        xp = levelUser["xp"]
        neededXp = await self.client.calculateLevelXp(level + 1) - await self.client.calculateLevelXp(level)
        levelXp = xp - await self.client.calculateLevelXp(level)

        await ctx.reply(f"## {member.name.capitalize()}\n" + f"Level {level}\n" + f"XP {format(levelXp, ',')} / {format(neededXp, ',')}")

    @commands.hybrid_command(
        name="rank",
        description="Get the level of a member or yourself",
        aliases=["level", "lvl"]
    )
    @app_commands.describe(
        member="The member to get the rank of",
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

        user_data = {
            "name": member.name.capitalize(),
            "xp": format(levelXp, ','),
            "next_level_xp": format(neededXp, ','),
            "level": level,
            "percentage": (levelXp / neededXp) * 100,
            "bar_color": "#6585ec"
        }

        background = Editor(Canvas((800, 250), color="#23272A"))
        profile_image = load_image(str(member.avatar))
        profile = Editor(profile_image).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        background.paste(profile, (25, 25))

        background.rectangle((25, 190), width=750, height=40, fill="#494b4f", radius=20)
        background.bar(
            (25, 190),
            max_width=750,
            height=40,
            percentage=user_data["percentage"],
            fill=user_data["bar_color"],
            radius=20,
        )
        background.text((200, 55), user_data["name"], font=poppins, color="white")

        background.text((200, 100), f"Level {user_data['level']}", font=poppins_small, color="white")

        background.text((200, 130), f"XP {user_data['xp']} / {user_data['next_level_xp']}", font=poppins_small, color="white")

        file = discord.File(fp=background.image_bytes, filename="card.png")

        await ctx.send(file=file)

    @commands.hybrid_command(
        name="leaderboard",
        with_app_command=True,
        description="Get the rank of a member",
        aliases=["lb", "levels"]
    )
    @app_commands.describe(
        page="The page you wanna view",
    )
    async def leaderboard(self, ctx: commands.Context, page: int = 1) -> None:
        limit = 10
        skip = (page - 1) * limit
        users = self.client.database.levels.find().sort("xp", -1).skip(skip).limit(limit)

        leaderboard_text = ""
        for index, user in enumerate(users):
            member = ctx.guild.get_member(user["user_id"])
            leaderboard_text += f"{index+1}. **{member.name}** - Level {user['level']} ({format(user['xp'], ',')} Xp)\n"

        if not leaderboard_text:
            await ctx.send("No users found on that page")
        else:
            await ctx.send(f"## Leaderboard - Page {page}\n" + leaderboard_text)

    @commands.hybrid_command(
        name="xp-for-level",
        with_app_command=True,
        description="Get the rank of a member",
        aliases=["for-level", "xfl", "xp-level"]
    )
    @app_commands.describe(
        level="Which level you wanna know the xp of",
    )
    async def xp_for_level(self, ctx: commands.Context, level: int) -> None:
        if level < 0:
            await ctx.send("Level must be greater than 0")
            return
        
        xp = await self.client.calculateLevelXp(level)
        await ctx.reply(f"Xp for level {level}: {format(xp, ',')}")
    

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
            neededXp = await self.client.calculateLevelXp(level + 1) - xp

            if (neededXp <= 0):
                level = levelUser["level"] + 1

                if self.client.config["levelUp"]["channel_id"]:
                    channel_id = self.client.config["levelUp"]["channel_id"]
                    channel = self.client.get_channel(channel_id)
                    if not channel or not channel.permissions_for(channel.guild.me).send_messages:
                        channel = message.channel
                else:
                    channel = message.channel

                if self.client.config["levelUp"]["enabled"] and self.client.config["levelUp"]["message"] and channel.permissions_for(channel.guild.me).send_messages:
                    await channel.send(self.client.config["levelUp"]["message"].replace("{user}", message.author.mention).replace("{level}", str(level)))   

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
                        "last_updated": datetime.datetime.now(),
                        "user_name": message.author.name
                    }
                }
            )
        else:
            self.client.database.levels.insert_one({
                "user_id": message.author.id,
                "guild_id": message.guild.id,
                "user_name": message.author.name,
                "xp": newXp,
                "level": 0,
                "last_updated": datetime.datetime.now()
            })

async def setup(client) -> None:
    await client.add_cog(Levels(client))