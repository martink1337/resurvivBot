import discord
from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rules(self, ctx):
        embed = discord.Embed(
            title="📜 Server Rules",
            description=(
                "1. Be polite and respect others.\n"
                "2. Do not spam or advertise without permission.\n"
                "3. Stick to channel topics.\n"
                "4. Don't use offensive words.\n"
                "5. Follow the moderators' instructions."
            ),
            color=0x00B037,
        )
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(Rules(bot))
