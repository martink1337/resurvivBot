import discord
from discord.ext import commands
import asyncio
import random
import re
from config import config  # Import the configuration

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staff_roles = config.get("staff_roles", []) # Load the roles from config

    def convert_time(self, time_str):
        # Converts time like 10s, 5m, 1h, 1d to seconds
        match = re.match(r"(\d+)(s|m|h|d)", time_str)
        if not match:
            return None
        amount, unit = int(match.group(1)), match.group(2)
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        return amount * multipliers[unit]

    @commands.command()
    async def giveaway(self, ctx, time: str = None, *, prize: str = None):
        # Check for role
        user_roles = [r.name.lower() for r in ctx.author.roles]
        if not any(role in user_roles for role in self.staff_roles):
            await ctx.send("You do not have the necessary rights to start a giveaway.")
            return

        if not time or not prize:
            await ctx.send("Please enter time and prize, example: `s!giveaway 1m Free Nitro`")
            return

        seconds = self.convert_time(time)
        if seconds is None:
            await ctx.send("Invalid time! Use formats like 10s, 5m, 1h, 1d.")
            return

        embed = discord.Embed(title="🎉 GIVEAWAY 🎉", description=f"Reward: **{prize}**\nReact with 🎉 to participate!", color=0x00B037)
        embed.set_footer(text=f"End after {time}")
        giveaway_message = await ctx.send(embed=embed)
        await giveaway_message.add_reaction("🎉")

        await asyncio.sleep(seconds)

        message = await ctx.channel.fetch_message(giveaway_message.id)
        users = set()
        for reaction in message.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.add(user)

        if len(users) == 0:
            await ctx.send("There are no participants in the raffle.")
            return

        winner = random.choice(list(users))
        await ctx.send(f"🎉 Congratulations {winner.mention}, you won **{prize}**! 🎉")

        try:
            await winner.send(f"Congratulations! You won a giveaway for: **{prize}** in the server {ctx.guild.name}")
        except:
            pass  # If you can't send him a DM

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
