from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def say(self, ctx, *, message: str):
        """Изпраща съобщение от името на бота."""
        await ctx.message.delete()  # Изтрива командата на потребителя
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Say(bot))
