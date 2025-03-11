import discord
from discord.ext import commands
import requests

class FortniteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def fetch_fortnite_shop(self):
        """Fetches and parses the Fortnite shop JSON from the API."""
        api_url = "https://fortnite-api.com/v2/shop"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
        except requests.RequestException as e:
            return f"Error fetching data: {e}"

        data = response.json()
        if "data" not in data or "entries" not in data["data"]:
            return "Invalid JSON format received from API."

        shop_items = []
        for entry in data["data"]["entries"]:
            if "brItems" in entry and entry["brItems"]:
                for item in entry["brItems"]:
                    item_details = {
                        "name": item.get("name", "Unknown Item"),
                        "description": item.get("description", "No description available"),
                        "type": item["type"].get("displayValue", "Unknown Type") if "type" in item else "N/A",
                        "rarity": item["rarity"].get("displayValue", "Unknown Rarity") if "rarity" in item else "N/A",
                        "set": item["set"].get("text", "No set info") if "set" in item else "N/A",
                        "introduced": item["introduction"].get("text", "Unknown") if "introduction" in item else "N/A",
                        "regular_price": entry.get("regularPrice", "N/A"),
                        "final_price": entry.get("finalPrice", "N/A"),
                        "giftable": "✅ Yes" if entry.get("giftable") else "❌ No",
                        "refundable": "✅ Yes" if entry.get("refundable") else "❌ No",
                        "image": item["images"].get("icon") if "images" in item else None
                    }
                    shop_items.append(item_details)
        return shop_items

    @commands.command(name="fetch_fortnite_shop")
    async def fetch_shop(self, ctx):
        """Fetches and displays the Fortnite shop details in multiple embeds."""
        shop_items = self.fetch_fortnite_shop()
        if isinstance(shop_items, str):  # Error message returned
            await ctx.send(shop_items)
            return
        if not shop_items:
            await ctx.send("No items found in the shop.")
            return
        for item in shop_items[:100]:
            embed = discord.Embed(title=f"🛒 {item['name']}", color=discord.Color.blue())
            embed.add_field(name="📝 Description", value=item["description"], inline=False)
            embed.add_field(name="📌 Type", value=item["type"], inline=True)
            embed.add_field(name="🌟 Rarity", value=item["rarity"], inline=True)
            embed.add_field(name="📦 Set", value=item["set"], inline=True)
            embed.add_field(name="📖 Introduced", value=item["introduced"], inline=True)
            embed.add_field(name="💰 Regular Price", value=f"{item['regular_price']} V-Bucks", inline=True)
            embed.add_field(name="🔥 Final Price", value=f"{item['final_price']} V-Bucks", inline=True)
            embed.add_field(name="🎁 Giftable", value=item["giftable"], inline=True)
            embed.add_field(name="🔄 Refundable", value=item["refundable"], inline=True)
            if item["image"]:
                embed.set_thumbnail(url=item["image"])
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FortniteCog(bot))
