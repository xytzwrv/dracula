import discord
from discord.ext import commands
from config import IGNORE_CHANNELS  # Import the list of channels to ignore for censorship

# Import helper functions from the utils package
from utils.helpers import get_emoji_str
from utils.file_io import save_json, load_json

REACTION_DATA_FILE = "reaction_data.json"

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_data = load_json(REACTION_DATA_FILE) or {}

    def save_data(self):
        """Saves the reaction data using the file_io utility."""
        save_json(REACTION_DATA_FILE, self.reaction_data)
        print("DEBUG: Reaction data saved.")

    @commands.command(name="rebuild_reactions")
    @commands.has_permissions(administrator=True)
    async def rebuild_reactions(self, ctx):
        """Reconstructs the reaction data from scratch."""
        await ctx.send("Starting reaction reconstruction. This may take some time...")
        self.reaction_data = {}
        self.save_data()
        print("DEBUG: Reaction database cleared.")
        total_messages_scanned = 0
        total_reactions_updated = 0
        for channel in ctx.guild.text_channels:
            try:
                async for message_obj in channel.history(limit=None):
                    total_messages_scanned += 1
                    msg_id = str(message_obj.id)
                    author_id = str(message_obj.author.id) if message_obj.author else "Unknown"
                    self.reaction_data[msg_id] = {"author_id": author_id, "reactions": {}}
                    for reaction in message_obj.reactions:
                        emoji_str = get_emoji_str(reaction.emoji)
                        self.reaction_data[msg_id]["reactions"][emoji_str] = {
                            "users_given": [],
                            "count_given": 0,
                            "users_received": [],
                            "count_received": 0
                        }
                        async for user in reaction.users():
                            user_id = str(user.id)
                            if user_id not in self.reaction_data[msg_id]["reactions"][emoji_str]["users_given"]:
                                self.reaction_data[msg_id]["reactions"][emoji_str]["users_given"].append(user_id)
                                self.reaction_data[msg_id]["reactions"][emoji_str]["count_given"] += 1
                            if user_id != author_id and user_id not in self.reaction_data[msg_id]["reactions"][emoji_str]["users_received"]:
                                self.reaction_data[msg_id]["reactions"][emoji_str]["users_received"].append(user_id)
                                self.reaction_data[msg_id]["reactions"][emoji_str]["count_received"] += 1
                            total_reactions_updated += 1
            except discord.Forbidden:
                continue
        self.save_data()
        await ctx.send(
            f"Reconstruction complete! Messages scanned: {total_messages_scanned}, "
            f"Reactions updated: {total_reactions_updated}"
        )

    @commands.command(name="print_credit")
    async def print_credit(self, ctx, member: discord.Member = None):
        """Prints the reaction credits (unique reactions received) for the member."""
        if member is None:
            member = ctx.author
        self.reaction_data = load_json(REACTION_DATA_FILE) or {}
        reactions_received = {}
        for message_id, info in self.reaction_data.items():
            if "author_id" not in info or "reactions" not in info:
                continue
            if str(info["author_id"]) == str(member.id):
                for emoji, details in info["reactions"].items():
                    unique_users = set(details["users_received"]) - {str(member.id)}
                    reactions_received[emoji] = reactions_received.get(emoji, 0) + len(unique_users)
        if not reactions_received:
            await ctx.send(f"**{member.display_name}** has not received any reactions.")
            return
        response = f"Reactions received by **{member.display_name}**:\n"
        for emoji, count in reactions_received.items():
            response += f"{emoji}: {count} unique users\n"
        await ctx.send(response)

    @commands.command(name="print_debit")
    async def print_debit(self, ctx, member: discord.Member = None):
        """Prints the reaction debits (reactions given) for the member."""
        if member is None:
            member = ctx.author
        self.reaction_data = load_json(REACTION_DATA_FILE) or {}
        reactions_given = {}
        for message_id, info in self.reaction_data.items():
            if "reactions" not in info:
                continue
            for emoji, details in info["reactions"].items():
                if str(member.id) in details["users_given"]:
                    reactions_given[emoji] = reactions_given.get(emoji, 0) + 1
        if not reactions_given:
            await ctx.send(f"**{member.display_name}** has not given any reactions.")
            return
        response = f"Reactions given by **{member.display_name}**:\n"
        for emoji, count in reactions_given.items():
            response += f"{emoji}: {count}\n"
        await ctx.send(response)

    @commands.command(name="print_balance")
    async def print_balance(self, ctx, member: discord.Member = None):
        """Prints the net reaction balance for the member."""
        if member is None:
            member = ctx.author
        self.reaction_data = load_json(REACTION_DATA_FILE) or {}
        balance = {}
        for message_id, message_info in self.reaction_data.items():
            if "reactions" not in message_info or "author_id" not in message_info:
                continue
            for emoji, details in message_info["reactions"].items():
                emoji_str = get_emoji_str(emoji)
                if str(message_info["author_id"]) == str(member.id):
                    received_count = len(set(details["users_received"]))
                else:
                    received_count = 0
                given_count = 1 if str(member.id) in details["users_given"] else 0
                net = received_count - given_count
                if net != 0:
                    balance[emoji_str] = balance.get(emoji_str, 0) + net
        if not balance:
            await ctx.send(f"**{member.display_name}** has no reaction balance.")
            return
        response = f"Reaction balance for **{member.display_name}**:\n"
        for emoji, count in balance.items():
            response += f"{emoji}: {count}\n"
        await ctx.send(response)

    def censor(self, message_content):
        """
        Censors the message content by replacing non-space characters with asterisks.
        Ignores censorship for messages from channels in the IGNORE_CHANNELS list.
        """
        # Ignore censorship for channels in IGNORE_CHANNELS
        if message_content.channel.name in IGNORE_CHANNELS:
            return message_content.content  # Return original message if in ignore channels

        # Censor the message
        censored_content = ''.join('*' if not char.isspace() else char for char in message_content.content)
        return censored_content

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
