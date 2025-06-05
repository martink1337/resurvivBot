import discord
from discord.ext import commands
from config import config  # Импортираме конфигурацията

class Sticky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky = {}  # {channel_id: {"text": str, "message": discord.Message}}
        self.staff_roles = config.get("staff_roles", [])

    @commands.Cog.listener()
    async def on_ready(self):
        print("Sticky Cog Loaded")

    @commands.command()
    async def sticky(self, ctx, *, message: str):
        """Активира sticky съобщение в канала"""

        user_roles = [r.name.lower() for r in ctx.author.roles]
        if not any(role in user_roles for role in self.staff_roles):
            await ctx.send("Нямаш нужните права да използваш тази команда.")
            return

        channel_id = ctx.channel.id

        if channel_id in self.sticky:
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass

        sticky_msg = await ctx.send(f"**Sticky:** {message}")
        self.sticky[channel_id] = {"text": message, "message": sticky_msg}
        await ctx.send("Sticky съобщението е настроено.")

    @commands.command()
    async def unsticky(self, ctx):
        """Деактивира sticky съобщението в този канал"""

        user_roles = [r.name.lower() for r in ctx.author.roles]
        if not any(role in user_roles for role in self.staff_roles):
            await ctx.send("Нямаш нужните права да използваш тази команда.")
            return

        channel_id = ctx.channel.id
        if channel_id in self.sticky:
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass
            del self.sticky[channel_id]
            await ctx.send("Sticky деактивирано в този канал.")
        else:
            await ctx.send("Няма активен sticky в този канал.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        if channel_id in self.sticky:
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass

            sticky_msg = await message.channel.send(f"**Sticky:** {self.sticky[channel_id]['text']}")
            self.sticky[channel_id]["message"] = sticky_msg

async def setup(bot):
    await bot.add_cog(Sticky(bot))
