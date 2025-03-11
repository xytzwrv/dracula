import discord
from discord.ext import commands
import subprocess
import os
import asyncio
import glob

class CrackifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.download_dir = "downloads"  # Directory to store downloaded songs
        os.makedirs(self.download_dir, exist_ok=True)

    @commands.command(name="crackify")
    async def crackify(self, ctx, spotify_url: str):
        """
        Downloads a song, album, or playlist from YouTube using a Spotify URL and sends it in Discord.
        """
        await ctx.send(f"🎵 Fetching `{spotify_url}` ... This may take a while.")

        # Run spotDL to download the song, album, or playlist
        cmd = ["spotdl", spotify_url, "--output", self.download_dir]
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await ctx.send(f"❌ Error downloading: {stderr.decode()}")
            return

        # Find downloaded files (MP3, FLAC, etc.)
        music_files = glob.glob(os.path.join(self.download_dir, "*.*"))

        if not music_files:
            await ctx.send("❌ No files found after download.")
            return

        await ctx.send(f"✅ Download complete! Uploading {len(music_files)} files...")

        # Send each file while respecting Discord's file size limit (25MB for free users, 50MB for Nitro)
        for file_path in music_files:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
            if file_size > 25:  # Check if file exceeds Discord's upload limit
                await ctx.send(f"⚠️ `{os.path.basename(file_path)}` is too large ({file_size:.2f}MB) to send via Discord.")
            else:
                try:
                    await ctx.send(file=discord.File(file_path))
                except Exception as e:
                    await ctx.send(f"❌ Failed to send `{os.path.basename(file_path)}`: {str(e)}")

            os.remove(file_path)  # Clean up file after sending

        await ctx.send("✅ All available songs have been sent!")

async def setup(bot):
    await bot.add_cog(CrackifyCog(bot))
