import discord
from discord.ext import commands
import os

# Load token from Railway environment variable
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is online and ready.")

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Load cogs if you use them
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(TOKEN)
