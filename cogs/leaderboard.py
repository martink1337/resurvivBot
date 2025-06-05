import discord
from discord.ext import commands
import requests
from config import config  # Your config module, from which you read the settings

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = config.get("leaderboard_api_url", "https://api.survev.io/api/leaderboard")

    @commands.command(name="soloinfo")
    async def soloinfo(self, ctx):
        await self.fetch_and_send_leaderboard(ctx, "solo")

    @commands.command(name="duoinfo")
    async def duoinfo(self, ctx):
        await self.fetch_and_send_leaderboard(ctx, "duo")

    async def fetch_and_send_leaderboard(self, ctx, team_mode):
        payload = {
            "type": "most_kills",
            "interval": "alltime",
            "teamMode": team_mode,
            "mapId": "0"
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                leaderboard = data
            else:
                leaderboard = data.get("leaderboard", [])

            if not leaderboard:
                await ctx.send("Няма данни в класацията.")
                return

            embed = discord.Embed(
                title=f"Топ 10 играчи по килове - {team_mode.capitalize()}",
                color=discord.Color.blue()
            )

            for i, player in enumerate(leaderboard[:10], start=1):
                if team_mode == "duo":
                    names = player.get("usernames", ["Unknown", "Unknown"])
                    name = f"{names[0]} & {names[1]}"
                else:
                    name = player.get("username", "Unknown")

                kills = player.get("val", 0)
                region = player.get("region", "unknown")

                embed.add_field(
                    name=f"{i}. {name}",
                    value=f"**Kills:** {kills}\n**Region:** {region}",
                    inline=False
                )

            await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            await ctx.send(f"Грешка при заявката: {e}")

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
