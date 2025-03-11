import os
from discord.ext import commands
from fuzzywuzzy import process

class FlowCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flow")
    async def flow(self, ctx, *, query: str):
        """
        Performs a fuzzy search on a text file (flow.txt) using fuzzywuzzy and returns
        the line that best matches the provided query.
        """
        flow_file = "flow.txt"  # Path to your text file

        if not os.path.exists(flow_file):
            await ctx.send("The flow file does not exist.")
            return

        try:
            with open(flow_file, "r", encoding="utf-8") as f:
                # Read all non-empty lines from the file.
                lines = [line.strip() for line in f if line.strip()]
        except Exception as e:
            await ctx.send(f"Error reading the flow file: {e}")
            return

        if not lines:
            await ctx.send("The flow file is empty.")
            return

        # Use fuzzywuzzy to find the best match for the query.
        # The extractOne function returns a tuple: (best_match, score, index).
        best_match = process.extractOne(query, lines)
        if best_match is None:
            await ctx.send("No matching line found.")
            return

        match, score, _ = best_match
        # Define a threshold to ensure the match is good enough.
        threshold = 30  # Adjust as necessary (score range is 0 to 100)
        if score < threshold:
            await ctx.send("No matching line found.")
        else:
            await ctx.send(f"Best match (score {score}): {match}")

async def setup(bot):
    await bot.add_cog(FlowCog(bot))
