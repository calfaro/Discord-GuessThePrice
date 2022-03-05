from disnake.ext import commands
from disnake import CommandInteraction, Embed
from utils.buttons import Confirm
from utils.html_header import fetch_url_meta
from tabulate import tabulate
from asyncio import sleep
from functools import reduce

# local imports
from utils.db import load_predictions, clear_predictions, dump_predictions


class Predictions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currencies = ["USD"]

    def find_max_with_limit(self, members, limit=None):
        """
        find the highest value in the list withoug going over the set limit
        if no values are below the limit, returns None
        """
        member_tuples = members.items()
        if limit:
            member_tuples = list(filter(lambda x: x[1] <= limit, member_tuples))
            if len(member_tuples) > 0:
                return reduce(lambda x, y: x if x[1] > y[1] else y, member_tuples)

    """
    Predictions slash commands group
    """

    @commands.slash_command(
        name="openbets",
        description="(Admin) Starts an event, enables /placebets command",
    )
    @commands.has_role("Admin")
    async def open_bets_command(self, inter, currency: str = "USD", url: str = None):
        """Openbets command - Admin only, creates the event and allows members to start placing bets on the event"""
        # update the "open" key value to True, allows /placebets to work
        data = await load_predictions()

        """check if prediction event is already enabled"""
        if data["open"] == True:
            await inter.response.send_message(
                f"There is already a prediction event in progress", ephemeral=True
            )
            return

        """if no prediction event active - reset prediction.json to default"""
        self.currencies = [currency.upper()]
        data["open"] = True
        data["currency"] = currency.upper()
        data["predictions"] = []
        await dump_predictions(data)

        """if all arguments are None, return the "command enabled" message"""
        if url is None:
            await inter.response.send_message(f"`/placebets` command is now enabled")
            return

        """if url string is present, defer the interaction response while fetching the meta tags"""
        await inter.response.defer()
        title, desc, banner = fetch_url_meta(url)

        """ build the embed for the event"""
        embed = Embed(
            title="Bets are open for the following event:",
            description=f"**Required Currency**: {currency}\n\n**{title}**\n{desc} -- ([Read more...]({url}))",
        )
        if not banner is None:
            embed.set_image(url=banner)

        """ send edit the original deferred message with the embed"""
        await inter.edit_original_message(embed=embed)

    @commands.slash_command(
        name="closebets", description="(Admin) Disable /placebet command"
    )
    @commands.has_role("Admin")
    async def closebets_command(self, inter):
        """Admin only command - closes the bets, disables /placebets command"""
        data = await load_predictions()
        if data["open"]:
            data["open"] = False
            await dump_predictions(data)
            await inter.response.send_message(
                "Bets have been closed. /placebets command has been disabled."
            )
        else:
            await inter.response.send_message(
                f"Bets are already closed.", ephemeral=True
            )

    @commands.slash_command(
        name="placebet", description="Place a prediction on an upcoming auction"
    )
    async def prediction(self, inter, currency: str, price: float):
        """
        Placebet command
        Allows the member to place a prediction on the current active event

        --Parameters--
        currency - a required string paramater (autofill selection based on currency enterd in openbet command
        price - the price prediction
        """
        author_id = str(inter.author.id)

        """load the json data and check if the bets are currently open"""
        data = await load_predictions()
        req_currency = data["currency"]
        if not data["open"]:
            await inter.response.send_message(
                "Predictions are currently closed. Check back once an admin has started a new event.",
                ephemeral=True,
            )
            return

        """if submitted currency does not match the required currency from json, result in error message"""
        if currency != req_currency and req_currency is not None:
            await inter.response.send_message(
                f"Your prediction must be in the correct currency: **{req_currency}**. Please try again.",
                ephemeral=True,
            )
            return

        """check if member has already submitted a prediction"""
        for member in data["predictions"]:
            if author_id in member.keys():
                await inter.response.send_message(
                    f"You've already placed a prediction on the current event.",
                    ephemeral=True,
                )
                return

        """send confirmation message to use - included Confirm view for button confirmation"""
        await inter.response.send_message(
            f"Please confirm your prediction of: {currency} {price:,.2f}",
            ephemeral=True,
            view=Confirm(currency, price),
        )

    @commands.slash_command(
        name="showbets", description="View currently placed predictions"
    )
    async def view_predictions(self, inter):
        """load the current predictions and format to embed - send message to channel"""
        guild = inter.guild
        data = await load_predictions()

        """if data['predictions'] is an empty list, send error message to interaction channel, return"""
        if not data["predictions"]:
            await inter.response.send_message(
                f"No predictions have been submitted.", ephemeral=True
            )
            return

        """append the member display name and currency, value data into a table for tabulate to format"""
        prediction_table_data = []

        for item in data["predictions"]:
            for key, value in item.items():
                member = guild.get_member(int(key))
                currency = value["currency"]
                value = value["value"]
                prediction_table_data.append(
                    [member.display_name, f"{currency} {value:,.2f}"]
                )

        """tabulate the list into a clean formatted table"""
        prediction_table = tabulate(
            prediction_table_data, tablefmt="plain", stralign="left", numalign="decimal"
        )

        """embed for showbets message"""
        embed = Embed(
            title="Current Predictions", description=f"```{prediction_table}```"
        )

        """send the embed to the interaction channel"""
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="finalprice",
        description="(Admin) Submit the final price - Bot replies with winner.",
    )
    @commands.has_role("Admin")
    async def final_price_command(self, inter, currency: str, real_price: float):
        """
        Admin only command  - Final price
        Allows an admin to submit the final price of the auctioned item from the event
        Bot will then sort and calculate the prediction entries and declare a winnner
        Bets are closed and the predictions.json is defaulted

        --Parameters--
        currency - a required string argument (from selection) that will match the currency used in openbets
        real_price - the required float argument that represents the final selling price of the auctioned piece.
        """
        guild = inter.guild

        """ load the data from json and ensure submission is with correct currency"""
        data = await load_predictions()
        req_currency = data["currency"]
        if currency != req_currency and req_currency is not None:
            await inter.response.send_message(
                f"Please submite the final price with the correct currency: {req_currency}",
                ephemeral=True,
            )
            return

        """sets the currencies list back to default 'USD' """
        self.currencies = ["USD"]

        """fetch all of the member predictions, sort, and declare the winning prediction"""
        member_predictions = {}

        """check if any predictions exist in the json file"""
        if not data["predictions"]:
            await inter.response.send_message(
                f"No predictions have been submitted.", ephemeral=True
            )
            return

        """if predictions exist, fetch those predictions and set them into a dict{member : prediction value}"""
        for item in data["predictions"]:
            for key, value in item.items():
                member = guild.get_member(int(key))
                value = value["value"]
                member_predictions[member.mention] = value

        """sort the predictions and find the winning prediction without going over the real price"""
        winner = self.find_max_with_limit(member_predictions, limit=real_price)

        """if no predictions were under the final value, no winner selected"""
        if winner is None:
            await inter.response.send_message(
                f"Looks like no predictions were close without going over {currency} {real_price}"
            )
            return

        """assign the winner and clear the predictions from json"""
        member, value = winner
        await clear_predictions()

        """build the winner announcement embed"""
        embed = Embed(
            title="Winner Winner!",
            description=f"**Final Value**:\n{currency} {real_price:,.2f}\n\n{member} wins with a prediction of {currency} {value:,.2f}!",
        )

        """defer the initial interaction response for 3 seconds - adds suspence  :D"""
        await inter.response.defer()
        await sleep(3)
        await inter.edit_original_message(embed=embed)

    """
    Admin command check errors
    """

    @closebets_command.error
    @open_bets_command.error
    @final_price_command.error
    async def missing_admin_error(self, inter, error):
        if isinstance(error, commands.MissingRole):
            await inter.response.send_message(
                f"You do not have the proper permissions to use this command",
                ephemeral=True,
            )
        else:
            raise error

    """
    Auto complete currency
    """

    @final_price_command.autocomplete("currency")
    # @open_bets_command.autocomplete("currency")
    @prediction.autocomplete("currency")
    async def currency_autocoplete(self, inter: CommandInteraction, string: str):
        """provide autocomplete selection for the /placebets command"""
        string = string.lower()
        return [currency for currency in self.currencies if string in currency.lower()]


def setup(bot):
    bot.add_cog(Predictions(bot))
