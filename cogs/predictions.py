from disnake.ext import commands
from disnake import CommandInteraction, Embed
from utils.buttons import Confirm
from tabulate import tabulate
from asyncio import sleep
from functools import reduce

# local imports
from utils.db import load_predictions, clear_predictions, dump_predictions


class Predictions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.currencies = ["USD", "HK"]

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
        description="(Admin) Enables /placebets command",
    )
    async def open_bets_command(
        self,
        *,
        inter,
        event_name: str = None,
        event_desc: str = None,
        event_url: str = None,
        img_url: str = None,
        currency: str = None,
    ):
        """Openbets command - Admin only, creates the event and allows members to start placing bets on the event"""
        # update the "open" key value to True, allows /placebets to work
        data = await load_predictions()
        data["open"] = True
        data["currency"] = currency
        data["predictions"] = []
        await dump_predictions(data)

        event_url.strip()
        img_url.strip()
        event_name.strip()
        event_desc.strip()

        embed = Embed(
            title=f"Predictions are open!",
            description=f"**{event_name}**\n{event_desc}\n([Read more...]({event_url}))",
        )
        embed.set_image(url=img_url)

        await inter.response.send_message(embed=embed)



    @commands.slash_command(name='closebets', description='(Admin) Disable /placebet command')
    async def closebets_command(self, inter):
        '''closes the bets, - disables /placebets command'''
        data = await load_predictions()
        if data['open']:
            data['open'] = False
            await dump_predictions(data)
            await inter.response.send_message('Bets have been closed. /placebets command has been disabled.')
        else:
            await inter.response.send_message(f'Bets are already cl')


    @commands.slash_command(
        name="placebet", description="Place a prediction on an upcoming auction"
    )
    async def prediction(self, inter, currency: str, price: float):
        """placebet command - store the author's ID, currency type, and prediction value in json

        --Arguments--
        currency - currency type to be submitted with the included value (string - autofills from autocomplete method below)
        value - the prediction value (float)
        """
        # check if interaction author already exists in predictions.json
        author_id = str(inter.author.id)
        data = await load_predictions()
        req_currency = data["currency"]
        if not data["open"]:
            await inter.response.send_message(
                "Predictions are currently closed. Check back once an admin has started a new event.", ephemeral=True
            )
            return

        if currency != req_currency:
            await inter.response.send_message(
                f"Your prediction must bein the correct currency: **{req_currency}**. Please try again.", ephemeral=True
            )
            return

        for member in data["predictions"]:
            if author_id in member.keys():
                await inter.response.send_message(
                    f"You've already placed a prediction on the current event.",
                    ephemeral=True,
                )
                return

        # send the confirmation check response
        await inter.response.send_message(
            f"Please confirm your prediction of:{currency} {price:,.2f}",
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

        # if data['predictions'] is an empty list, send error message to interaction channel, return
        if not data["predictions"]:
            await inter.response.send_message(
                f"No predictions have been submitted.", ephemeral=True
            )
            return

        # prepare data for embed
        prediction_table_data = []

        for item in data["predictions"]:
            for key, value in item.items():
                member = guild.get_member(int(key))
                currency = value["currency"]
                value = value["value"]
                prediction_table_data.append(
                    [member.display_name, f"{currency} {value:,.2f}"]
                )

        # tabulate the list into a clean table
        prediction_table = tabulate(
            prediction_table_data, tablefmt="plain", stralign="left", numalign="decimal"
        )

        # build the embed
        embed = Embed(
            title="Current Predictions", description=f"```{prediction_table}```"
        )

        # send the formatted embed to the command channel
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="finalprice",
        description="(Admin) Submit the final price - Bot replies with winner.",
    )
    async def final_price_command(self, inter, currency: str, real_price: float):
        """Admin can submit the final price to the bot - compares member predictions with final price and displays the winner"""
        guild = inter.guild
        data = await load_predictions()
        member_predictions = {}

        if not data["predictions"]:
            await inter.response.send_message(
                f"No predictions have been submitted.", ephemeral=True
            )
            return
        # fetch the member ids and prediction values
        for item in data["predictions"]:
            for key, value in item.items():
                member = guild.get_member(int(key))
                value = value["value"]
                member_predictions[member.mention] = value

        # find the winning value and member - highest prediction without going over
        winner = self.find_max_with_limit(member_predictions, limit=real_price)

        if winner is None:
            await inter.response.send_message(
                f"Looks like no predictions were close without going over {currency} {real_price}"
            )

        else:
            member, value = winner
            # await clear_predictions()

            embed = Embed(
                title="Winner Winner!",
                description=f"The final value was {currency} {real_price:,.2f}",
            )
            embed.add_field(
                name="Winner(s):", value=f"{member} with a prediction of {value:,.2f}"
            )

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
        if instance(error, MissingRole):
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
    @open_bets_command.autocomplete("currency")
    @prediction.autocomplete("currency")
    async def currency_autocoplete(self, inter: CommandInteraction, string: str):
        """provide autocomplete selection for the /placebets command"""
        string = string.lower()
        return [currency for currency in self.currencies if string in currency.lower()]


def setup(bot):
    bot.add_cog(Predictions(bot))
