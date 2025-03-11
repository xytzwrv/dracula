import os
import discord
from discord.ext import commands
import yt_dlp

class Y2MP3Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="y2mp3")
    async def download_audio(self, ctx, url: str):
        """Downloads audio from a YouTube link and sends it back."""
        await ctx.send("Downloading audio... Please wait.")
        
        output_dir = "downloads"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_name = f"{output_dir}/{info['title']}.mp3"
        
            if os.path.exists(file_name):
                await ctx.send("Download complete! Here's your audio:", file=discord.File(file_name))
                os.remove(file_name)  # Cleanup after sending
            else:
                await ctx.send("Failed to process the audio file.")
        
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Y2MP3Cog(bot))
