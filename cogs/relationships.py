import discord
from discord.ext import commands
from discord import app_commands

from utils.tree_image import generate_tree_image
from database.database import db


# --------------------------------------------------
# MAIN COG
# --------------------------------------------------

class Relationships(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------
    # ADD RELATIONSHIP (NON-SPOUSE)
    # --------------------------------------------------

    @app_commands.command(
        name="addrelationship",
        description="Add a relationship to your tree."
    )
    @app_commands.describe(
        partner="The user you want to add",
        rtype="spouse / caregiver / little / middle / sibling / handler / pet"
    )
    async def addrelationship(
        self,
        interaction: discord.Interaction,
        partner: discord.Member,
        rtype: str
    ):

        rtype = rtype.lower()
        valid = ["spouse", "caregiver", "little", "middle", "sibling", "handler", "pet"]

        if rtype not in valid:
            return await interaction.response.send_message(
                "❌ Invalid type. Use: spouse, caregiver, little, middle, sibling, handler, pet",
                ephemeral=True
            )

        # For spouse, use /marry instead
        if rtype == "spouse":
            return await interaction.response.send_message(
                "❌ Use `/marry` to add a spouse.",
                ephemeral=True
            )

        async with db.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO relationships (user_id, partner_id, relationship_type)
                VALUES ($1, $2, $3)
                """,
                interaction.user.id,
                partner.id,
                rtype,
            )

        await interaction.response.send_message(
            f"✅ Added **{rtype}**: {partner.display_name}",
            ephemeral=True
        )

    # --------------------------------------------------
    # REMOVE RELATIONSHIP
    # --------------------------------------------------

    @app_commands.command(
        name="removerelationship",
        description="Remove a relationship from your tree."
    )
    async def removerelationship(
        self,
        interaction: discord.Interaction,
        partner: discord.Member
    ):

        async with db.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM relationships
                WHERE user_id = $1 AND partner_id = $2
                """,
                interaction.user.id,
                partner.id,
            )

        # result is like "DELETE 0" or "DELETE 1"
        if result == "DELETE 0":
            return await interaction.response.send_message(
                "❌ That user was not in your tree.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"🗑 Removed {partner.display_name} from your tree.",
            ephemeral=True
        )

    # --------------------------------------------------
    # MARRY COMMAND (SIMPLE MUTUAL, ONE SPOUSE EACH)
    # --------------------------------------------------

    @app_commands.command(
        name="marry",
        description="Marry another user (one spouse each)."
    )
    @app_commands.describe(
        partner="The user you want to marry"
    )
    async def marry(
        self,
        interaction: discord.Interaction,
        partner: discord.Member
    ):

        if partner.id == interaction.user.id:
            return await interaction.response.send_message(
                "❌ You cannot marry yourself.",
                ephemeral=True
            )

        if partner.bot:
            return await interaction.response.send_message(
                "❌ You cannot marry a bot.",
                ephemeral=True
            )

        async with db.pool.acquire() as conn:
            # Check if either user is already married
            existing = await conn.fetchrow(
                """
                SELECT *
                FROM marriages
                WHERE (user1_id = $1 OR user2_id = $1)
                   OR (user1_id = $2 OR user2_id = $2)
                """,
                interaction.user.id,
                partner.id,
            )

            if existing:
                return await interaction.response.send_message(
                    "❌ One of you is already married.",
                    ephemeral=True
                )

            # Create marriage row
            await conn.execute(
                """
                INSERT INTO marriages (user1_id, user2_id)
                VALUES ($1, $2)
                """,
                interaction.user.id,
                partner.id,
            )

            # Add spouse relationship for both users
            await conn.execute(
                """
                INSERT INTO relationships (user_id, partner_id, relationship_type)
                VALUES ($1, $2, 'spouse'),
                       ($2, $1, 'spouse')
                """,
                interaction.user.id,
                partner.id,
            )

        await interaction.response.send_message(
            f"💍 {interaction.user.mention} is now married to {partner.mention}!",
            ephemeral=False
        )

    # --------------------------------------------------
    # DIVORCE COMMAND
    # --------------------------------------------------

    @app_commands.command(
        name="divorce",
        description="Divorce your current spouse."
    )
    async def divorce(
        self,
        interaction: discord.Interaction
    ):

        async with db.pool.acquire() as conn:
            marriage = await conn.fetchrow(
                """
                SELECT *
                FROM marriages
                WHERE user1_id = $1 OR user2_id = $1
                """,
                interaction.user.id,
            )

            if not marriage:
                return await interaction.response.send_message(
                    "❌ You are not currently married.",
                    ephemeral=True
                )

            user1 = marriage["user1_id"]
            user2 = marriage["user2_id"]

            # Delete marriage
            await conn.execute(
                """
                DELETE FROM marriages
                WHERE id = $1
                """,
                marriage["id"],
            )

            # Delete spouse relationships for both
            await conn.execute(
                """
                DELETE FROM relationships
                WHERE (user_id = $1 AND partner_id = $2 AND relationship_type = 'spouse')
                   OR (user_id = $2 AND partner_id = $1 AND relationship_type = 'spouse')
                """,
                user1,
                user2,
            )

        # Try to resolve partner for message
        partner = interaction.guild.get_member(user2) if user1 == interaction.user.id else interaction.guild.get_member(user1)

        if partner:
            msg = f"💔 {interaction.user.mention} is now divorced from {partner.mention}."
        else:
            msg = "💔 Divorce complete."

        await interaction.response.send_message(
            msg,
            ephemeral=False
        )

    # --------------------------------------------------
    # TREE COMMAND (USES RELATIONSHIPS TABLE)
    # --------------------------------------------------

    @app_commands.command(
        name="tree",
        description="Generate your pastel family tree."
    )
    async def tree(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None
    ):

        await interaction.response.defer()

        target = user or interaction.user

        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT partner_id, relationship_type
                FROM relationships
                WHERE user_id = $1
                """,
                target.id,
            )

        spouse = None
        caregivers = []
        littles = []
        middles = []
        siblings = []
        handler = None
        pets = []

        for row in rows:
            partner = interaction.guild.get_member(row["partner_id"])
            if not partner:
                continue

            rtype = row["relationship_type"]

            if rtype == "spouse":
                spouse = partner.display_name
            elif rtype == "caregiver":
                caregivers.append(partner.display_name)
            elif rtype == "little":
                littles.append(partner.display_name)
            elif rtype == "middle":
                middles.append(partner.display_name)
            elif rtype == "sibling":
                siblings.append(partner.display_name)
            elif rtype == "handler":
                handler = partner.display_name
            elif rtype == "pet":
                pets.append(partner.display_name)

        jpeg_bytes = generate_tree_image(
            user_name=target.display_name,
            spouse_name=spouse,
            caregivers=caregivers,
            littles=littles,
            middles=middles,
            siblings=siblings,
            handler=handler,
            pets=pets,
        )

        file = discord.File(jpeg_bytes, filename="family_tree.jpg")

        await interaction.followup.send(
            f"🌳 Cute pastel family tree for {target.mention}:",
            file=file
        )


async def setup(bot):
    await bot.add_cog(Relationships(bot))
