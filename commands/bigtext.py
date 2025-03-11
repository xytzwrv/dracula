import discord
from discord.ext import commands, tasks
import os
import pyfiglet
from gtts import gTTS
from pydub import AudioSegment
from config import BIGTEXT_ANON_CHANNEL_ID, MOD_LOG
from utils.helpers import censor  # Import the censor function

# Global variables
messages_buffer = []  # Buffer to store messages
instant_mode = False  # To toggle instant mode on/off

class BigTextCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # Store the bot instance
        # Start the background task to flush every 10 minutes.
        self.auto_flush_task.start()

    def cog_unload(self):
        # Cancel the background task when the cog is unloaded.
        self.auto_flush_task.cancel()

    def text_to_speech(self, text, filename):
        """Converts text to speech and saves it as an MP3 file."""
        tts = gTTS(text)
        tts.save(filename)

    def merge_audio_files(self, audio_files, output_file):
        """Merges multiple MP3 files into one."""
        combined = AudioSegment.empty()
        for file in audio_files:
            audio = AudioSegment.from_file(file)
            combined += audio
        combined.export(output_file, format="mp3")

    async def flush_buffer(self):
        """
        Merges buffered 4-character DM messages into a single audio file and posts it 
        to the BIGTEXT_ANON_CHANNEL_ID, then clears the buffer.
        """
        global messages_buffer
        if not messages_buffer:
            return
        channel = self.bot.get_channel(BIGTEXT_ANON_CHANNEL_ID)
        if not channel:
            print("ERROR: Big text anon channel not found.")
            messages_buffer.clear()
            return
        audio_files = []
        for idx, (text, user_id) in enumerate(messages_buffer):
            filename = f"/tmp/message_{idx}.mp3"
            self.text_to_speech(text, filename)
            audio_files.append(filename)
        output_file = "/tmp/combined_messages.mp3"
        self.merge_audio_files(audio_files, output_file)
        await channel.send(file=discord.File(output_file))
        for f in audio_files:
            os.remove(f)
        os.remove(output_file)
        messages_buffer.clear()

    @tasks.loop(minutes=10)
    async def auto_flush_task(self):
        """Every 10 minutes (if not in instant mode) flush the buffered messages to TTS audio."""
        if instant_mode:
            return
        if not messages_buffer:
            return
        await self.flush_buffer()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots.
        if message.author.bot:
            return

        # ---------- DM Handling ----------
        if isinstance(message.channel, discord.DMChannel):
            content = message.content.strip()
            if len(content) == 4:
                try:
                    # If content is exactly 4 characters, render ASCII art and post to channel
                    art_text = pyfiglet.figlet_format(content)
                    target_channel = self.bot.get_channel(BIGTEXT_ANON_CHANNEL_ID)
                    if target_channel is None:
                        await message.channel.send("Error: Target channel not found.")
                        return
                    await target_channel.send(f"```{art_text}```")
                    await message.channel.send("Your 4-character ASCII art has been posted anonymously!")

                    # Handle TTS logic based on instant_mode
                    if instant_mode:
                        filename = f"/tmp/{message.author.id}_instant.mp3"
                        self.text_to_speech(content, filename)
                        await target_channel.send(file=discord.File(filename))
                        os.remove(filename)
                    else:
                        # Buffer message for later processing
                        messages_buffer.append((content, message.author.id))

                    # Flush the buffer if the message is "over"
                    if content.lower() == "over":
                        await self.flush_buffer()

                except Exception as e:
                    await message.channel.send(f"Error generating art: {e}")

            else:
                # Use censor function to handle invalid content
                censored = censor(message)
                censored_display = f"```\n{censored}\n```"
                mod_log_channel = self.bot.get_channel(MOD_LOG)
                if mod_log_channel:
                    await mod_log_channel.send(f"Failed anonymous DM submission from {message.author}:\n{censored_display}")
                await message.channel.send("Invalid input. Please send exactly four characters.")
            return
        # Do nothing if the message is not a DM
        return

    @commands.command(name="flush")
    @commands.has_permissions(administrator=True)
    async def flush_cmd(self, ctx):
        """Immediately flushes the batch of buffered DM messages (if any)."""
        if not messages_buffer:
            await ctx.send("No messages in the batch to flush.")
            return
        await self.flush_buffer()
        await ctx.send("Batch flushed successfully.")

    @commands.command(name="toggle_instant_mode")
    @commands.has_permissions(administrator=True)
    async def toggle_instant_mode_cmd(self, ctx):
        """
        Toggles instant_mode on/off.
        When ON, every valid 4-char DM is immediately converted to TTS audio and posted.
        When OFF, messages are batched every 10 minutes.
        """
        global instant_mode
        instant_mode = not instant_mode
        state = "ON" if instant_mode else "OFF"
        await ctx.send(f"Instant mode is now **{state}**.")

async def setup(bot):
    await bot.add_cog(BigTextCog(bot))
