import discord
from discord.ext import commands
import re
import requests
from io import BytesIO
from utils.gif_tools import overlay_text_on_gif

class RemixCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remix")
    async def remix(self, ctx, font: str, *, overlay_text: str):
        """
        Remixes a GIF by overlaying the specified text.
        To use, reply to a message containing a GIF (attachment, link, or embed).
        """
        if not ctx.message.reference:
            await ctx.send("Please reply to a message containing a GIF (attachment, link, or embed).")
            return
        try:
            replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except Exception:
            await ctx.send("Could not fetch the replied message.")
            return

        gif_data = None
        # Check for an attached GIF.
        if replied_message.attachments:
            for attachment in replied_message.attachments:
                if attachment.filename.lower().endswith('.gif'):
                    try:
                        gif_data = await attachment.read()
                    except Exception:
                        await ctx.send("Failed to read the attached GIF.")
                        return
                    break

        # If no attachment, look for a URL in the message content.
        gif_url = None
        if gif_data is None:
            match = re.search(r'(https?://\S+\.gif)', replied_message.content, re.IGNORECASE)
            if match:
                gif_url = match.group(1)

        # Check embeds if still no data.
        if gif_data is None and not gif_url and replied_message.embeds:
            for embed in replied_message.embeds:
                if embed.image and embed.image.url:
                    gif_url = embed.image.url
                    break
                elif embed.thumbnail and embed.thumbnail.url:
                    gif_url = embed.thumbnail.url
                    break

        if gif_data is None and gif_url:
            if "tenor.com" in gif_url and not gif_url.endswith('.gif'):
                gif_url += ".gif"
            response = requests.get(gif_url)
            if response.status_code != 200:
                await ctx.send("Failed to download the GIF.")
                return
            gif_data = response.content

        if gif_data is None:
            await ctx.send("The replied message does not contain a valid GIF attachment, link, or embed.")
            return

        try:
            remixed_buffer = overlay_text_on_gif(gif_data, font, overlay_text)
        except Exception as e:
            await ctx.send(f"Error processing GIF: {e}")
            return

        await ctx.send(file=discord.File(remixed_buffer, filename="remixed.gif"))

async def setup(bot):
    await bot.add_cog(RemixCog(bot))
