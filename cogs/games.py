from database.games import (
    get_game_state,
    save_counting,
    save_wordchain,
    save_settings,
)


# --------------------------------------------------
# MAIN COG
# --------------------------------------------------

class Games(commands.Cog):
    def __init__(self, bot):
    self.bot = bot
    async def get_data(self, guild: discord.Guild):
    return await get_game_state(guild.id)

    # --------------------------------------------------
    # COUNTING COMMAND
    # --------------------------------------------------

    @app_commands.command(name="counting", description="Configure the counting game")
    @app_commands.describe(
        setchannel="Select the counting channel",
        toggle="Enable or disable counting"
    )
    async def counting(
        self,
        interaction: discord.Interaction,
        setchannel: discord.TextChannel | None,
        toggle: bool | None
    ):
        if setchannel is not None:
            self.data["counting_channel"] = setchannel.id
            save_data(self.data)
            await interaction.response.send_message(
                f"📌 Counting channel set to <#{setchannel.id}>",
                ephemeral=True
            )
            return

        if toggle is not None:
            self.data["counting_enabled"] = toggle
            save_data(self.data)
            await interaction.response.send_message(
                f"Counting game is now **{'enabled' if toggle else 'disabled'}**.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "❌ You must specify at least one option.",
            ephemeral=True
        )

    # --------------------------------------------------
    # WORDCHAIN COMMAND
    # --------------------------------------------------

    @app_commands.command(name="wordchain", description="Configure the word-chain game")
    @app_commands.describe(
        setchannel="Select the word-chain channel",
        toggle="Enable or disable word-chain"
    )
    async def wordchain(
        self,
        interaction: discord.Interaction,
        setchannel: discord.TextChannel | None,
        toggle: bool | None
    ):
        if setchannel is not None:
            self.data["wordchain_channel"] = setchannel.id
            save_data(self.data)
            await interaction.response.send_message(
                f"📌 Word-chain channel set to <#{setchannel.id}>",
                ephemeral=True
            )
            return

        if toggle is not None:
            self.data["wordchain_enabled"] = toggle
            save_data(self.data)
            await interaction.response.send_message(
                f"Word-chain game is now **{'enabled' if toggle else 'disabled'}**.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "❌ You must specify at least one option.",
            ephemeral=True
        )

    # --------------------------------------------------
    # MESSAGE LISTENER
    # --------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        # -------------------------
        # COUNTING LOGIC
        # -------------------------

        if (
            self.data["counting_enabled"] and
            self.data["counting_channel"] and
            message.channel.id == self.data["counting_channel"]
        ):

            try:
                number = int(message.content)
            except ValueError:
                await message.channel.send(f"{message.author.mention} ❌ Not a number! Count reset to 0.")
                self.data["current_count"] = 0
                self.data["last_counter"] = None
                save_data(self.data)
                return

            if message.author.id == self.data["last_counter"]:
                await message.channel.send(
                    f"{message.author.mention} ❌ You cannot count twice in a row! Reset to 0."
                )
                self.data["current_count"] = 0
                self.data["last_counter"] = None
                save_data(self.data)
                return

            if number == self.data["current_count"] + 1:
                self.data["current_count"] += 1
                self.data["last_counter"] = message.author.id
                save_data(self.data)
                await message.add_reaction("✅")
            else:
                await message.channel.send(
                    f"{message.author.mention} ❌ Wrong number! Expected **{self.data['current_count'] + 1}**. Reset to 0."
                )
                self.data["current_count"] = 0
                self.data["last_counter"] = None
                save_data(self.data)

        # -------------------------
        # WORDCHAIN LOGIC
        # -------------------------

        if (
            self.data["wordchain_enabled"] and
            self.data["wordchain_channel"] and
            message.channel.id == self.data["wordchain_channel"]
        ):

            word = message.content.lower().strip()

            if message.author.id == self.data["word_last_counter"]:
                await message.channel.send(
                    f"{message.author.mention} ❌ You cannot play twice in a row! Chain reset."
                )
                self.data["last_word"] = ""
                self.data["used_words"] = []
                self.data["word_last_counter"] = None
                save_data(self.data)
                return

            if word in self.data["used_words"]:
                await message.channel.send(
                    f"{message.author.mention} ❌ That word was already used! Chain reset."
                )
                self.data["last_word"] = ""
                self.data["used_words"] = []
                self.data["word_last_counter"] = None
                save_data(self.data)
                return

            if self.data["last_word"] == "":
                self.data["last_word"] = word
                self.data["used_words"].append(word)
                self.data["word_last_counter"] = message.author.id
                save_data(self.data)
                await message.add_reaction("🟦")
                return

            if word[0] != self.data["last_word"][-1]:
                await message.channel.send(
                    f"{message.author.mention} ❌ Wrong letter! "
                    f"Word must start with **{self.data['last_word'][-1]}**. Chain reset."
                )
                self.data["last_word"] = ""
                self.data["used_words"] = []
                self.data["word_last_counter"] = None
                save_data(self.data)
                return

            self.data["last_word"] = word
            self.data["used_words"].append(word)
            self.data["word_last_counter"] = message.author.id
            save_data(self.data)
            await message.add_reaction("🟩")


# --------------------------------------------------
# SETUP
# --------------------------------------------------

async def setup(bot):
    await bot.add_cog(Games(bot))
