import os
import discord
from discord.ext import commands

class FileHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        MP3 = 123456789012345678  # Replace with the actual channel ID

        if message.channel.id == MP3:
            allowed = False

            # Check if message has attachments and if they are audio files
            if message.attachments:
                for attachment in message.attachments:
                    filename = attachment.filename.lower()
                    if filename.endswith('.mp3') or filename.endswith('.wav'):
                        allowed = True
                        break

            # Check if the message mentions anyone
            if message.mentions:
                allowed = True

            # If the message isn't allowed, delete it
            if not allowed:
                await message.delete()
                return

            # Check for duplicate filenames and save attachments
            for attachment in message.attachments:
                filename = attachment.filename.lower()
                if filename.endswith('.mp3'):
                    folder = "mp3"
                elif filename.endswith('.wav'):
                    folder = "wav"
                else:
                    continue

                if not os.path.exists(folder):
                    os.makedirs(folder)

                file_path = os.path.join(folder, attachment.filename)

                if os.path.exists(file_path):
                    await message.channel.send(f"Duplicate filename detected: **{attachment.filename}**. Please rename your file and try again.")
                    await message.delete()
                    return

            # Save the attachments to the appropriate folder
            for attachment in message.attachments:
                filename = attachment.filename.lower()
                if filename.endswith('.mp3'):
                    folder = "mp3"
                elif filename.endswith('.wav'):
                    folder = "wav"
                else:
                    continue

                if not os.path.exists(folder):
                    os.makedirs(folder)

                file_path = os.path.join(folder, attachment.filename)
                await attachment.save(file_path)
                print(f"Saved {attachment.filename} to the {folder} folder.")

# Setup the cog
async def setup(bot):
    await bot.add_cog(FileHandler(bot))