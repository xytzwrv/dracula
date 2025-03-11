import discord
from discord.ext import commands
import os
import config
from config import TOKEN

bot = commands.Bot(command_prefix="Dracula ", intents=discord.Intents.all())

async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            extension = f"commands.{filename[:-3]}"
            print(f"Loading extension: {extension}")
            try:
                await bot.load_extension(extension)  # Must await if the cog uses async setup
            except Exception as e:
                print(f"Error loading {extension}: {e}")

@bot.command(name="reloadcogs")
@commands.is_owner()
async def reload_cogs(ctx):
    """Reloads all cogs from the commands folder."""
    errors = []
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            extension = f"commands.{filename[:-3]}"
            try:
                await bot.reload_extension(extension)  # Must await in 2.x
                print(f"Reloaded extension: {extension}")
            except Exception as e:
                errors.append(f"Failed to reload {extension}: {e}")
    if errors:
        await ctx.send("Some errors occurred:\n" + "\n".join(errors))
    else:
        await ctx.send("Successfully reloaded all cogs.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

async def main():
    # Load cogs, then start the bot
    await load_extensions()
    await bot.start(config.TOKEN)  # or your token of choice

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
