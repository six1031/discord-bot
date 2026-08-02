import discord
from discord.ext import commands
import os
import asyncio

# --------------------------------------------------
# BOT SETUP
# --------------------------------------------------

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# --------------------------------------------------
# READY EVENT + SLASH COMMAND SYNC
# --------------------------------------------------

@bot.event
async def on_ready():
    bot.add_view(CloseTicketButton())  # persistent button support
    print(f"Logged in as {bot.user}")
    print("Bot is online and ready.")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# --------------------------------------------------
# EXAMPLE PREFIX COMMAND
# --------------------------------------------------

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


# --------------------------------------------------
# ASYNC COG LOADER (REQUIRED FOR DISCORD.PY 2.x)
# --------------------------------------------------

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")


# --------------------------------------------------
# MAIN STARTUP (REQUIRED FOR RAILWAY)
# --------------------------------------------------

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


asyncio.run(main())
