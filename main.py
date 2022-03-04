from disnake import Intents
from disnake.ext import commands
from dotenv import load_dotenv
from os import getenv, listdir


def load_extensions():
    """iterate through files in /cogs and load them as bot extensions"""
    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


if __name__ == "__main__":

    # instantiate the bot and declare intents
    intents = Intents.default()
    intents.members = True

    bot = commands.Bot(intents=intents, test_guilds=[947543739671412878])

    @bot.listen()
    async def on_ready():
        print(f"{bot.user} is alive and listening for Discord events.")

    load_extensions()
    load_dotenv()
    bot.run(getenv("TOKEN"))
