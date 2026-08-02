import discord

from database.tickets import (
    create_ticket,
    has_open_ticket,
)

STAFF_ROLE_ID = 1428444870766231622
TICKET_CATEGORY_ID = 1526141859213086841


# --------------------------------------------------
# CLOSE BUTTON
# --------------------------------------------------

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Close Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ Only staff can close tickets.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "🗑 Closing ticket...",
            ephemeral=True
        )

        await interaction.channel.delete()


# --------------------------------------------------
# BASE TICKET VIEW
# --------------------------------------------------

class BaseTicketView(discord.ui.View):

    ticket_type = ""
    button_label = ""
    button_emoji = ""
    custom_id = ""

    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction):

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            return await interaction.response.send_message(
                "❌ Ticket category not found.",
                ephemeral=True
            )

        # Prevent duplicate tickets
        existing = discord.utils.get(
            category.channels,
            topic=f"{self.ticket_type}:{interaction.user.id}"
        )

        if existing:
            return await interaction.response.send_message(
                f"You already have an open {self.ticket_type} ticket:\n{existing.mention}",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            ),
            guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            )
        }

        channel = await category.create_text_channel(
            name=f"{self.ticket_type}-{interaction.user.name}",
            topic=f"{self.ticket_type}:{interaction.user.id}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"{self.button_emoji} {self.button_label}",
            colour=discord.Colour.blurple()
        )

        if self.ticket_type == "verification":
            embed.description = (
                "Welcome!\n\n"
                "Please answer the verification questions and upload your ID "
                "(cover everything except your photo and DOB)."
            )

        elif self.ticket_type == "reports":
            embed.description = (
                "Please explain:\n"
                "• Who are you reporting?\n"
                "• What happened?\n"
                "• When did it happen?\n"
                "• Evidence/screenshots"
            )

        elif self.ticket_type == "applications":
            embed.description = (
                "Thank you for applying!\n\n"
                "Please answer the staff application questions."
            )

        elif self.ticket_type == "contact":
            embed.description = (
                "Tell us how we can help and a staff member will respond shortly."
            )

        await channel.send(
            interaction.user.mention,
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )


# --------------------------------------------------
# VERIFICATION
# --------------------------------------------------

class VerificationTicketView(BaseTicketView):

    ticket_type = "verification"
    button_label = "Open Verification Ticket"
    button_emoji = "🪪"

    @discord.ui.button(
        label="Open Verification Ticket",
        style=discord.ButtonStyle.success,
        emoji="🪪",
        custom_id="ticket_verification"
    )
    async def button(self, interaction, button):
        await self.create_ticket(interaction)


# --------------------------------------------------
# REPORTS
# --------------------------------------------------

class ReportsTicketView(BaseTicketView):

    ticket_type = "reports"
    button_label = "Open Report Ticket"
    button_emoji = "⚠️"

    @discord.ui.button(
        label="Open Report Ticket",
        style=discord.ButtonStyle.danger,
        emoji="⚠️",
        custom_id="ticket_reports"
    )
    async def button(self, interaction, button):
        await self.create_ticket(interaction)


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

class ApplicationsTicketView(BaseTicketView):

    ticket_type = "applications"
    button_label = "Apply For Staff"
    button_emoji = "📝"

    @discord.ui.button(
        label="Apply For Staff",
        style=discord.ButtonStyle.primary,
        emoji="📝",
        custom_id="ticket_applications"
    )
    async def button(self, interaction, button):
        await self.create_ticket(interaction)


# --------------------------------------------------
# CONTACT
# --------------------------------------------------

class ContactTicketView(BaseTicketView):

    ticket_type = "contact"
    button_label = "Contact Staff"
    button_emoji = "💌"

    @discord.ui.button(
        label="Contact Staff",
        style=discord.ButtonStyle.secondary,
        emoji="💌",
        custom_id="ticket_contact"
    )
    async def button(self, interaction, button):
        await self.create_ticket(interaction)
