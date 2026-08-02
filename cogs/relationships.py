import discord
from discord.ext import commands
from discord import app_commands

from utils.tree_image import generate_tree_image

# --------------------------------------------------
# RELATIONSHIP STORAGE (JSON)
# --------------------------------------------------

import json
import os

REL_FILE = "data/relationships.json"

def load_relationships():
    if not os.path.exists(REL_FILE):
        return {}
    with open(REL_FILE, "r") as f:
        return json.load(f)

def save_relationships(data):
    with open(REL_FILE, "w") as f:
        json.dump(data, f, indent=4)

relationships = load_relationships()


# --------------------------------------------------
# HELPER: GET RELATIONSHIPS FOR USER
# --------------------------------------------------

def get_relationships_for(user_id: int):
    user_id = str(user_id)
    if user_id not in relationships:
        return []
    return relationships[user_id]


# --------------------------------------------------
# MAIN COG
# --------------------------------------------------

class Relationships(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------
    # ADD RELATIONSHIP
    # --------------------------------------------------

    @app_commands.command(name="addrelationship", description="Add a relationship to your tree.")
    @app_commands.describe(
        partner="The user you want to add",
        rtype="spouse / caregiver / little / middle / sibling / handler / pet"
    )
    async def addrelationship(self, interaction: discord.Interaction, partner: discord.Member, rtype: str):

        rtype = rtype.lower()
        valid = ["spouse", "caregiver", "little", "middle", "sibling", "handler", "pet"]

        if rtype not in valid:
            return await interaction.response.send_message(
                "❌ Invalid type. Use: spouse, caregiver, little, middle, sibling, handler, pet",
                ephemeral=True
            )

        uid = str(interaction.user.id)

        if uid not in relationships:
            relationships[uid] = []

        relationships[uid].append({
            "partner_id": partner.id,
            "type": rtype
        })

        save_relationships(relationships)

        await interaction.response.send_message(
            f"✅ Added **{rtype}**: {partner.display_name}",
            ephemeral=True
        )

    # --------------------------------------------------
    # REMOVE RELATIONSHIP
    # --------------------------------------------------

    @app_commands.command(name="removerelationship", description="Remove a relationship.")
    async def removerelationship(self, interaction: discord.Interaction, partner: discord.Member):

        uid = str(interaction.user.id)

        if uid not in relationships:
            return await interaction.response.send_message(
                "❌ You have no relationships.",
                ephemeral=True
            )

        before = len(relationships[uid])
        relationships[uid] = [r for r in relationships[uid] if r["partner_id"] != partner.id]
        after = len(relationships[uid])

        save_relationships(relationships)

        if before == after:
            return await interaction.response.send_message(
                "❌ That user was not in your tree.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"🗑 Removed {partner.display_name} from your tree.",
            ephemeral=True
        )

    # --------------------------------------------------
    # TREE COMMAND (FULL WORKING VERSION)
    # --------------------------------------------------

    @app_commands.command(name="tree", description="Generate your pastel family tree.")
    async def tree(self, interaction: discord.Interaction, user: discord.Member = None):

        # Prevent Discord timeout
        await interaction.response.defer()

        target = user or interaction.user

        # Load relationships
        rels = get_relationships_for(target.id)

        spouse = None
        caregivers = []
        littles = []
        middles = []
        siblings = []
        handler = None
        pets = []

        for r in rels:
            partner = interaction.guild.get_member(r["partner_id"])
            if not partner:
                continue

            if r["type"] == "spouse":
                spouse = partner.display_name
            elif r["type"] == "caregiver":
                caregivers.append(partner.display_name)
            elif r["type"] == "little":
                littles.append(partner.display_name)
            elif r["type"] == "middle":
                middles.append(partner.display_name)
            elif r["type"] == "sibling":
                siblings.append(partner.display_name)
            elif r["type"] == "handler":
                handler = partner.display_name
            elif r["type"] == "pet":
                pets.append(partner.display_name)

        # Generate JPEG
        jpeg_bytes = generate_tree_image(
            user_name=target.display_name,
            spouse_name=spouse,
            caregivers=caregivers,
            littles=littles,
            middles=middles,
            siblings=siblings,
            handler=handler,
            pets=pets
        )

        file = discord.File(jpeg_bytes, filename="family_tree.jpg")

        await interaction.followup.send(
            f"🌳 Cute pastel family tree for {target.mention}:",
            file=file
        )


async def setup(bot):
    await bot.add_cog(Relationships(bot))
