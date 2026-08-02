import discord
from discord.ext import commands
from discord import app_commands

from utils.ticket_storage import load_panels, save_panels
panels = load_panels()


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

TICKET_CATEGORY_ID = 1526141859213086841   # ACTIVE TICKETS CATEGORY
STAFF_ROLE_ID = 1428444870766231622        # STAFF ROLE

panels = load_panels()  # Load saved ticket panels


# --------------------------------------------------
# CLOSE BUTTON
# --------------------------------------------------

class CloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Close Ticket",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket_button"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ Only staff can close tickets.",
                ephemeral=True
            )

        await interaction.channel.delete()



# --------------------------------------------------
# CREATE TICKET BUTTON (same as your original)
# --------------------------------------------------

class CreateTicketButton(discord.ui.View):
    def __init__(self, panel_type: str):
        super().__init__(timeout=None)
        self.panel_type = panel_type

    @discord.ui.button(
        label="🎫 Open Ticket",
        style=discord.ButtonStyle.green,
        custom_id="open_ticket_button"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            return await interaction.response.send_message(
                "❌ Ticket category not found.",
                ephemeral=True
            )

        ticket_channel = await category.create_text_channel(
            name=f"{self.panel_type}-ticket-{interaction.user.name}",
            topic=f"{self.panel_type.capitalize()} ticket for {interaction.user}",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        # --------------------------------------------------
        # PANEL-SPECIFIC EMBEDS
        # --------------------------------------------------

        if self.panel_type == "verification":
            embed = discord.Embed(
                title="🎫 Verification Ticket",
                description=(
                    f"Hi {interaction.user.mention}, thanks for opening a verification ticket.\n\n"
                    "Please answer the questions below:\n"
                    "1. What is your date of birth?\n"
                    "2. How old are you?\n"
                    "3. What is little space to you?\n"
                    "4. Why did you join our community?\n"
                    "5. Are you a regressor, caregiver, or supporter?\n"
                    "6. Explain one server rule.\n"
                    "7. How do you stay safe online?\n"
                    "8. What are your boundaries?\n"
                    "9. How should people interact with you?\n"
                    "10. Anything else staff should know?\n\n"
                    "**🪪 ID Requirement:**\n"
                    "Upload an ID with everything covered except your date of birth and photo."
                ),
                color=discord.Color.blue()
            )

        elif self.panel_type == "reports":
            embed = discord.Embed(
                title="⚠ Report Ticket",
                description=(
                    f"Thank you for opening a report ticket, {interaction.user.mention}.\n\n"
                    "Please provide:\n"
                    "1. Who/what you're reporting\n"
                    "2. What happened\n"
                    "3. When it happened\n"
                    "4. Where it happened\n"
                    "5. Evidence/screenshots\n"
                    "6. Has this happened before?\n"
                    "7. Anything else staff should know\n\n"
                    "**🔒 Confidential:** Only staff can see this."
                ),
                color=discord.Color.red()
            )

        elif self.panel_type == "applications":
            embed = discord.Embed(
                title="📝 Staff Application Ticket",
                description=(
                    f"Thanks for applying, {interaction.user.mention}!\n\n"
                    "Please answer:\n"
                    "1. Discord username\n"
                    "2. Age\n"
                    "3. Timezone\n"
                    "4. Activity level\n"
                    "5. Past staff experience\n"
                    "6. Why you want to join staff\n"
                    "7. What makes you a good moderator\n"
                    "8. Handling disagreements\n"
                    "9. Handling rule-breaking\n"
                    "10. Handling stress\n"
                    "11. Anything else we should know"
                ),
                color=discord.Color.orange()
            )

        elif self.panel_type == "contact":
            embed = discord.Embed(
                title="💌 Contact Staff Ticket",
                description=(
                    f"Hi {interaction.user.mention}, thanks for contacting staff!\n\n"
                    "Please tell us:\n"
                    "1. What you need help with\n"
                    "2. Details of your issue\n"
                    "3. Screenshots/info if needed\n\n"
                    "A staff member will respond soon 💙"
                ),
                color=discord.Color.purple()
            )

        await ticket_channel.send(embed=embed, view=CloseTicketButton())

        await interaction.response.send_message(
            f"✅ Your {self.panel_type} ticket has been created: {ticket_channel.mention}",
            ephemeral=True
        )


# --------------------------------------------------
# DROPDOWN SELECTOR FOR PANEL TYPE
# --------------------------------------------------

class PanelSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Verification", value="verification", emoji="🪪"),
            discord.SelectOption(label="Reports", value="reports", emoji="⚠"),
            discord.SelectOption(label="Applications", value="applications", emoji="📝"),
            discord.SelectOption(label="Contact Staff", value="contact", emoji="💌"),
        ]

        super().__init__(
            placeholder="Choose a ticket panel type...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        panel_type = self.values[0]

        embed = discord.Embed(
            title=f"🎫 {panel_type.capitalize()} Tickets",
            description="Click the button below to open a ticket.",
            color=discord.Color.green()
        )

        view = CreateTicketButton(panel_type)

        msg = await interaction.channel.send(embed=embed, view=view)

        # Save panel permanently
        panels["panels"].append({
            "channel_id": interaction.channel.id,
            "message_id": msg.id,
            "type": panel_type
        })
        save_panels(panels)

        await interaction.response.send_message(
            f"Panel created for **{panel_type}**.",
            ephemeral=True
        )


class PanelSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PanelSelect())


# --------------------------------------------------
# MAIN COG
# --------------------------------------------------

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketpanel", description="Create a ticket panel with a dropdown selector.")
    async def ticketpanel(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🎫 Pillow Palace Ticket Panel",
            description="Choose the type of ticket panel you want to create:",
            color=discord.Color.blurple()
        )

        view = PanelSelectView()

        await interaction.response.send_message(
            "Select a panel type below.",
            ephemeral=True
        )

        await interaction.channel.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
