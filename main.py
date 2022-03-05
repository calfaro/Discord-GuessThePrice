'''
GuessThePrice - A simple predicion bot for NFT auctions

--Requirements--
- Python 3.9+
- Disnake 2.4+
- Tabulate 0.8.9
- python-dotenv 0.19.2
- bs4 0.0.1
- requests 2.27.1


COMMANDS
- /openbets - admin only, allows members to start submitting predictions on the event
- /placebet - members submit their prediction, stored in predictions.json
- /showbets - pulls the list of members and their predictions currently stored and displays in a clean table
- /closebets - admin only, disables the /placebet command - results in an error message
- /finalprice - admin only, admin submits the final outcome/price of the event and the bot calculates the winner that was closest without going over.


'''

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
