import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Optional, Literal

# ============================================================
# SIMPLE IN-MEMORY STORAGE (Replace with DB later)
# ============================================================

RELATIONSHIPS = []   # active relationships
HISTORY = []         # past relationships


def add_relationship(rel_type: str, user_id: int, partner_id: int, initiated_by: int, accepted_by: int):
    RELATIONSHIPS.append({
        "type": rel_type,
        "user_id": user_id,
        "partner_id": partner_id,
        "started_at": datetime.utcnow(),
        "initiated_by": initiated_by,
        "accepted_by": accepted_by,
    })


def remove_relationship(rel_type: str, user_id: int, partner_id: int, reason: str, removed_by: int):
    global RELATIONSHIPS
    new_list = []

    for r in RELATIONSHIPS:
        if r["type"] == rel_type and r["user_id"] == user_id and r["partner_id"] == partner_id:
            HISTORY.append({
                **r,
                "ended_at": datetime.utcnow(),
                "reason": reason,
                "removed_by": removed_by,
            })
        else:
            new_list.append(r)

    RELATIONSHIPS = new_list


def get_relationships_for(user_id: int):
    return [r for r in RELATIONSHIPS if r["user_id"] == user_id]


def has_relationship(rel_type: str, user_id: int, partner_id: int):
    return any(
        r for r in RELATIONSHIPS
        if r["type"] == rel_type and r["user_id"] == user_id and r["partner_id"] == partner_id
    )


def get_spouse(user_id: int) -> Optional[int]:
    for r in RELATIONSHIPS:
        if r["type"] == "spouse" and r["user_id"] == user_id:
            return r["partner_id"]
    return None


# ============================================================
# RESTRICTIONS
# ============================================================

def is_bot(member: discord.Member):
    return member.bot


def can_marry(user: discord.Member, partner: discord.Member):
    if is_bot(partner):
        return False, "You can't marry bots."
    if user.id == partner.id:
        return False, "You can't marry yourself."
    if get_spouse(user.id) is not None:
        return False, "You can only have one spouse."
    if get_spouse(partner.id) is not None:
        return False, "That user is already married."

    forbidden = ["caregiver", "little", "middle", "pet", "sibling"]

    for r in RELATIONSHIPS:
        if r["user_id"] == user.id and r["partner_id"] == partner.id and r["type"] in forbidden:
            return False, f"You can't marry your {r['type']}."
        if r["user_id"] == partner.id and r["partner_id"] == user.id and r["type"] in forbidden:
            return False, f"You can't marry someone who is your {r['type']}."

    return True, ""


# ============================================================
# ACCEPTANCE BUTTONS
# ============================================================

class RelationshipRequestView(discord.ui.View):
    def __init__(self, rel_type: str, requester: discord.Member, target: discord.Member):
        super().__init__(timeout=60)
        self.rel_type = rel_type
        self.requester = requester
        self.target = target

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.target.id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="💖")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        add_relationship(
            self.rel_type,
            self.requester.id,
            self.target.id,
            self.requester.id,
            self.target.id
        )

        # mirror for symmetric relationships
        if self.rel_type in ["spouse", "sibling"]:
            add_relationship(
                self.rel_type,
                self.target.id,
                self.requester.id,
                self.requester.id,
                self.target.id
            )

        await interaction.response.edit_message(
            content=f"💖 {self.target.mention} accepted the **{self.rel_type}** request from {self.requester.mention}!",
            view=None
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="💔")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content=f"💔 {self.target.mention} declined the **{self.rel_type}** request.",
            view=None
        )


# ============================================================
# MAIN COG
# ============================================================

class RelationshipsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --------------------------
    # MARRIAGE
    # --------------------------

    @app_commands.command(name="marry", description="Send a marriage request.")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        ok, msg = can_marry(interaction.user, user)
        if not ok:
            await interaction.response.send_message(f"🚫 {msg}", ephemeral=True)
            return

        view = RelationshipRequestView("spouse", interaction.user, user)
        await interaction.response.send_message(
            f"🌸 {user.mention}, {interaction.user.mention} wants to marry you!",
            view=view
        )

    @app_commands.command(name="divorce", description="Divorce your spouse.")
    async def divorce(self, interaction: discord.Interaction, user: discord.Member):
        if not has_relationship("spouse", interaction.user.id, user.id):
            await interaction.response.send_message("You are not married to that user.", ephemeral=True)
            return

        remove_relationship("spouse", interaction.user.id, user.id, "divorce", interaction.user.id)
        remove_relationship("spouse", user.id, interaction.user.id, "divorce", interaction.user.id)

        await interaction.response.send_message(
            f"💔 {interaction.user.mention} divorced {user.mention}."
        )

    # --------------------------
    # CAREGIVER / LITTLE / MIDDLE
    # --------------------------

    @app_commands.command(name="caregiver_add", description="Send a caregiver request.")
    async def caregiver_add(self, interaction: discord.Interaction, user: discord.Member):
        view = RelationshipRequestView("caregiver", interaction.user, user)
        await interaction.response.send_message(
            f"🧸 {user.mention}, {interaction.user.mention} wants to be your **Caregiver**.",
            view=view
        )

    @app_commands.command(name="little_add", description="Send a little request.")
    async def little_add(self, interaction: discord.Interaction, user: discord.Member):
        view = RelationshipRequestView("little", interaction.user, user)
        await interaction.response.send_message(
            f"🍼 {user.mention}, {interaction.user.mention} wants you as their **Little**.",
            view=view
        )

    @app_commands.command(name="middle_add", description="Send a middle request.")
    async def middle_add(self, interaction: discord.Interaction, user: discord.Member):
        view = RelationshipRequestView("middle", interaction.user, user)
        await interaction.response.send_message(
            f"🌙 {user.mention}, {interaction.user.mention} wants you as their **Middle**.",
            view=view
        )

    # --------------------------
    # SIBLING
    # --------------------------

    @app_commands.command(name="sibling_add", description="Send a sibling request.")
    async def sibling_add(self, interaction: discord.Interaction, user: discord.Member,
                          kind: Literal["brother", "sister"]):
        view = RelationshipRequestView("sibling", interaction.user, user)
        await interaction.response.send_message(
            f"🌼 {user.mention}, {interaction.user.mention} wants to be your **{kind.capitalize()}**.",
            view=view
        )

    # --------------------------
    # HANDLER / PET
    # --------------------------

    @app_commands.command(name="handler_add", description="Send a handler request.")
    async def handler_add(self, interaction: discord.Interaction, user: discord.Member):
        view = RelationshipRequestView("handler", interaction.user, user)
        await interaction.response.send_message(
            f"🎗️ {user.mention}, {interaction.user.mention} wants to be your **Handler**.",
            view=view
        )

    @app_commands.command(name="pet_add", description="Send a pet request.")
    async def pet_add(self, interaction: discord.Interaction, user: discord.Member):
        view = RelationshipRequestView("pet", interaction.user, user)
        await interaction.response.send_message(
            f"🐾 {user.mention}, {interaction.user.mention} wants you as their **Pet**.",
            view=view
        )

    # --------------------------
    # FAMILY TREE (JPEG ONLY)
    # --------------------------

    @app_commands.command(name="tree", description="Generate your pastel family tree.")
    async def tree(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user

        # Placeholder image — replace with generated JPEG later
        file = discord.File("family_tree_example.jpg", filename="family_tree.jpg")

        await interaction.response.send_message(
            f"🌳 Cute pastel family tree for {target.mention}:",
            file=file
        )


async def setup(bot):
    await bot.add_cog(RelationshipsCog(bot))
