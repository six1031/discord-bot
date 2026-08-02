import discord
from discord.ext import commands
from discord import app_commands

from utils.ticket_storage import load_panels, save_panels

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

        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(
                "❌ Only staff can close tickets.",
                ephemeral=True
            )

        await interaction.channel.delete()


# --------------------------------------------------
# TICKET TYPE BUTTONS (Report / Contact / Application / Verification)
# --------------------------------------------------

class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚠ Report", style=discord.ButtonStyle.danger, emoji="⚠")
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "reports")

    @discord.ui.button(label="💌 Contact Staff", style=discord.ButtonStyle.primary, emoji="💌")
    async def contact(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "contact")

    @discord.ui.button(label="📝 Applications", style=discord.ButtonStyle.success, emoji="📝")
    async def applications(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "applications")

    @discord.ui.button(label="🪪 Verification", style=discord.ButtonStyle.secondary, emoji="🪪")
    async def verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "verification")

    async def create_ticket(self, interaction, ticket_type):

        category = interaction.guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            return await interaction.response.send_message(
                "❌ Ticket category not found.",
                ephemeral=True
            )

        channel = await category.create_text_channel(
            name=f"{ticket_type}-{interaction.user.name}",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        # --------------------------------------------------
        # PANEL-SPECIFIC EMBEDS
        # --------------------------------------------------

        if ticket_type == "verification":
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

        elif ticket_type == "reports":
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

        elif ticket_type == "applications":
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

        elif ticket_type == "contact":
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

        await channel.send(embed=embed, view=CloseTicketButton())

        await interaction.response.send_message(
            f"✅ Your {ticket_type} ticket has been created: {channel.mention}",
            ephemeral=True
        )


# --------------------------------------------------
# MAIN COG
# --------------------------------------------------

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketpanel", description="Create a ticket panel with buttons.")
    async def ticketpanel(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🎫 Pillow Palace Ticket Panel",
            description="Choose the type of ticket you want to open:",
            color=discord.Color.green()
        )

        view = TicketTypeView()

        msg = await interaction.channel.send(embed=embed, view=view)

        # Save panel permanently
        panels["panels"].append({
            "channel_id": interaction.channel.id,
            "message_id": msg.id
        })
        save_panels(panels)

        await interaction.response.send_message(
            "Ticket panel created successfully.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
