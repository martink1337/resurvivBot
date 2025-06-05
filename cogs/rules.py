import discord
from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rules(self, ctx):
        embed = discord.Embed(
            title="📜 Правила на сървъра",
            description=(
                "1. Бъди учтив и уважавай останалите.\n"
                "2. Не спам и не рекламирай без позволение.\n"
                "3. Спазвай темите на каналите.\n"
                "4. Не използвай обидни думи.\n"
                "5. Следвай указанията на модераторите."
            ),
            color=0x00B037,
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(Rules(bot))
