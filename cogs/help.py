import discord
from discord.ext import commands

class Help(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        commandList = [
            "!8ball",
            "!avatar",
            "!join-date",
            "!leaderboard",
            "!members",
            "!ping",
            "!rank",
            "!self-timeout",
            "!xp",
            "!xp-for-level"
        ]
        
        #for command in self.context.bot.commands:
            #if command.hidden:
                #continue
            #commandList.append(f"{self.context.bot.config["prefix"]}{command.name}")


        await self.get_destination().send("## Commands\n" + "\n".join(commandList))

async def setup(client) -> None:
    client.help_command = Help()