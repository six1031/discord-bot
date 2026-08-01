import discord
import json
from discord.ext import commands

# --------------------------------------------------
# LOAD TOKEN
# --------------------------------------------------

with open("data/bot_token.json", "r") as f:
    TOKEN = json.load(f)["token"]

# --------------------------------------------------
# INTENTS
# --------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --------------------------------------------------
# IMPORT VIEWS FOR PERSISTENCE
# --------------------------------------------------

from cogs.tickets import CloseTicketButton, CreateTicketButton

# --------------------------------------------------
# SETUP HOOK
# --------------------------------------------------

async def setup_hook():
    # Load cogs FIRST
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.autothread")
    await bot.load_extension("cogs.games")
    await bot.load_extension("cogs.tickets")

    # Register persistent views AFTER cogs are loaded
    bot.add_view(CloseTicketButton())
    bot.add_view(CreateTicketButton("verification"))
    bot.add_view(CreateTicketButton("reports"))
    bot.add_view(CreateTicketButton("applications"))
    bot.add_view(CreateTicketButton("contact"))

    # Sync commands
    await bot.tree.sync()
    print("Slash commands synced.")

bot.setup_hook = setup_hook

# --------------------------------------------------
# EVENTS
# --------------------------------------------------

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print("Guilds:", bot.guilds)

@bot.command()
async def cogs(ctx):
    loaded = list(bot.extensions.keys())
    await ctx.send(f"Loaded cogs: {loaded}")

# --------------------------------------------------
# RUN BOT
# --------------------------------------------------

bot.run(TOKEN)
