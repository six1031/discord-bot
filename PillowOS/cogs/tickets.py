import discord
from discord.ext import commands
from discord import app_commands

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

TICKET_CATEGORY_ID = 1526141859213086841   # ACTIVE TICKETS CATEGORY
STAFF_ROLE_ID = 1428444870766231622        # STAFF ROLE


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
# CREATE TICKET BUTTON (DYNAMIC PER PANEL)
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
                    "To keep our community safe and comfy, please answer the questions below.\n"
                    "You may cover everything on your ID **except your date of birth and your photo**.\n\n"
                    "**Verification Questions:**\n"
                    "1. What is your date of birth?\n"
                    "2. How old are you right now?\n"
                    "3. What is little space to you?\n"
                    "4. What brings you to our Little Space community?\n"
                    "5. Are you joining as a regressor, caregiver, or supporter?\n"
                    "6. Pick one server rule and explain it in your own words.\n"
                    "7. Tell us one way you keep yourself safe online.\n"
                    "8. What are your personal boundaries or things you’re not comfy with?\n"
                    "9. How do you prefer people to interact with you in the server?\n"
                    "10. Anything else staff should know?\n\n"
                    "**🪪 ID Requirement:**\n"
                    "Upload a photo of your ID with everything covered except your date of birth and your photo."
                ),
                color=discord.Color.blue()
            )

        elif self.panel_type == "reports":
            embed = discord.Embed(
                title="⚠ General Report Ticket",
                description=(
                    f"Thank you for opening a report ticket, {interaction.user.mention}.\n\n"
                    "Please provide as much detail as possible so staff can review your report properly.\n\n"
                    "**Report Information Needed:**\n"
                    "1. Who or what are you reporting?\n"
                    "2. What happened? Describe clearly.\n"
                    "3. When did this happen?\n"
                    "4. Where did it happen? (Channel, DM, VC, etc.)\n"
                    "5. Any screenshots or evidence?\n"
                    "6. Has this happened before?\n"
                    "7. Anything else staff should know?\n\n"
                    "**🔒 Confidentiality:**\n"
                    "Your report is private and only visible to staff."
                ),
                color=discord.Color.red()
            )

        elif self.panel_type == "applications":
            embed = discord.Embed(
                title="📝 Staff Application Ticket",
                description=(
                    f"Thanks for applying to join the Pillow Palace Staff Team, {interaction.user.mention}!\n\n"
                    "Please answer the questions below as thoroughly and honestly as possible.\n\n"
                    "**Application Questions:**\n"
                    "1. What is your Discord username?\n"
                    "2. How old are you?\n"
                    "3. What timezone are you in?\n"
                    "4. How active can you be each week?\n"
                    "5. Have you staffed elsewhere before?\n"
                    "6. Why do you want to join Pillow Palace staff?\n"
                    "7. What qualities make you a good moderator?\n"
                    "8. How would you handle a disagreement?\n"
                    "9. How would you respond to rule-breaking?\n"
                    "10. How do you handle stressful situations?\n"
                    "11. Anything else we should know?\n\n"
                    "**📌 Before You Submit:**\n"
                    "- Be honest.\n"
                    "- Take your time.\n"
                    "- Staff must remain respectful and impartial.\n\n"
                    "Management will review your application soon. Good luck! 🍀"
                ),
                color=discord.Color.orange()
            )

        elif self.panel_type == "contact":
            embed = discord.Embed(
                title="💌 Contact Staff Ticket",
                description=(
                    f"Hi {interaction.user.mention}, thanks for contacting the Pillow Palace Staff Team!\n\n"
                    "Please provide the following information:\n\n"
                    "**What We Need From You:**\n"
                    "1. What do you need help with?\n"
                    "2. Describe your question or issue in detail.\n"
                    "3. Attach screenshots or info if needed.\n\n"
                    "**💙 Keep in Mind:**\n"
                    "- Staff are volunteers; response times may vary.\n"
                    "- Be respectful.\n"
                    "- More detail = faster help.\n\n"
                    "A staff member will respond as soon as possible. 💙"
                ),
                color=discord.Color.purple()
            )

        # Send embed + close button
        await ticket_channel.send(embed=embed, view=CloseTicketButton())

        await interaction.response.send_message(
            f"✅ Your {self.panel_type} ticket has been created: {ticket_channel.mention}",
            ephemeral=True
        )


# --------------------------------------------------
# MAIN COG
# --------------------------------------------------

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketpanel", description="Create a ticket panel in this channel.")
    @app_commands.describe(
        panel_type="verification / reports / applications / contact"
    )
    async def ticketpanel(self, interaction: discord.Interaction, panel_type: str):

        panel_type = panel_type.lower()

        if panel_type not in ["verification", "reports", "applications", "contact"]:
            return await interaction.response.send_message(
                "❌ Invalid panel type. Use: verification, reports, applications, contact",
                ephemeral=True
            )

        embed = discord.Embed(
            title=f"🎫 {panel_type.capitalize()} Tickets",
            description="Click the button below to open a ticket.\nA staff member will assist you shortly.",
            color=discord.Color.green()
        )

        view = CreateTicketButton(panel_type)

        await interaction.response.send_message(
            f"{panel_type.capitalize()} ticket panel created.",
            ephemeral=True
        )

        await interaction.channel.send(embed=embed, view=view)

    @app_commands.command(name="testticket", description="Send a test ticket button.")
    async def testticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Test Ticket Button",
            description="Click the button below. If it responds, your ticket system is working.",
            color=discord.Color.blurple()
        )

        view = CreateTicketButton("test")

        await interaction.response.send_message("Test ticket button sent.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)



async def setup(bot):
    await bot.add_cog(Tickets(bot))
