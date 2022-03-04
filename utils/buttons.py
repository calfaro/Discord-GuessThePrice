from disnake.ui import View, button, Button
from disnake import ButtonStyle, Interaction
from utils.db import load_predictions, dump_predictions


class Confirm(View):
    def __init__(self, currency, price):
        super().__init__(timeout=20)
        self.currency = currency
        self.price = price

    @button(label="Confirm", style=ButtonStyle.success)
    async def confirm_button(self, button: Button, interaction: Interaction):
        """Confirm the prediction and store in json - predictions.json"""
        data = await load_predictions()
        member_id = str(interaction.author.id)

        # append the new predictions to predictions list
        data["predictions"].append(
            {member_id: {"currency": self.currency, "value": self.price}}
        )

        # write the new data to predictions.json
        await dump_predictions(data)

        # complete interaction by editing the original confirmation message
        await interaction.response.send_message(
            "Your prediction has been confirmed and stored.", ephemeral=True
        )
        self.stop()

    @button(label="Cancel", style=ButtonStyle.danger)
    async def cancel_button(self, button: Button, interaction: Interaction):
        """Cancel the prediction - send cancellation response to interaction author"""
        await interaction.response.send_message(
            "You prediction has been cancelled.", ephemeral=True
        )
        self.stop()
