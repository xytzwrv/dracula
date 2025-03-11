# cogs/book_lookup.py

import discord
from discord.ext import commands
import isbnlib

class BookLookup(commands.Cog):
    """Cog for looking up book information by ISBN."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='isbn')
    async def fetch_book_info(self, ctx, *, isbn: str):
        """Fetches and displays book information based on the provided ISBN."""
        try:
            # Validate and canonicalize the ISBN
            isbn = isbnlib.canonical(isbn)
            if not isbnlib.is_isbn10(isbn) and not isbnlib.is_isbn13(isbn):
                await ctx.send("Invalid ISBN provided.")
                return

            # Fetch book metadata
            meta = isbnlib.meta(isbn)
            if not meta:
                await ctx.send("No metadata found for the provided ISBN.")
                return

            # Extract relevant information
            title = meta.get('Title', 'N/A')
            authors = ', '.join(meta.get('Authors', []))
            publisher = meta.get('Publisher', 'N/A')
            year = meta.get('Year', 'N/A')

            # Fetch cover image URL
            cover = isbnlib.cover(isbn)
            cover_url = cover.get('thumbnail') if cover else None

            # Create an embed message
            embed = discord.Embed(title=title, description=f"**Authors:** {authors}", color=0x00ff00)
            embed.add_field(name="Publisher", value=publisher, inline=False)
            embed.add_field(name="Year", value=year, inline=False)
            if cover_url:
                embed.set_thumbnail(url=cover_url)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
async def setup(bot):
    await bot.add_cog(BookLookup(bot))
