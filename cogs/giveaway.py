import discord
from discord.ext import commands, tasks
import asyncio
import random
import re

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def convert_time(self, time_str):
        # Конвертира време като 10s, 5m, 1h в секунди
        match = re.match(r"(\d+)(s|m|h|d)", time_str)
        if not match:
            return None
        amount, unit = int(match.group(1)), match.group(2)
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        return amount * multipliers[unit]

    @commands.command()
    async def giveaway(self, ctx, time: str = None, *, prize: str = None):
        if not time or not prize:
            await ctx.send("Моля, въведи време и награда, пример: `s!giveaway 1m Безплатно нитро`")
            return

        seconds = self.convert_time(time)
        if seconds is None:
            await ctx.send("Невалидно време! Използвай формати като 10s, 5m, 1h, 1d.")
            return

        embed = discord.Embed(title="🎉 GIVEAWAY 🎉", description=f"Награда: **{prize}**\nРеагирайте с 🎉 за участие!", color=0x00B037)
        embed.set_footer(text=f"Край след {time}")
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
            await ctx.send("Няма участници в томболата.")
            return

        winner = random.choice(list(users))
        await ctx.send(f"🎉 Поздравления {winner.mention}, ти спечели **{prize}**! 🎉")

        try:
            await winner.send(f"Честито! Ти спечели giveaway за: **{prize}** в сървъра {ctx.guild.name}")
        except:
            pass  # Ако не може да му се изпрати ЛС

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
