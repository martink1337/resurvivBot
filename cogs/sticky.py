import discord
from discord.ext import commands

class Sticky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ще пазим за всеки канал sticky съобщението (текст и съобщение обект)
        self.sticky = {}  # {channel_id: {"text": str, "message": discord.Message}}

    # ot tuk
    @commands.Cog.listener()
    async def on_ready(self):
        print("Sticky Cog Loaded")
    # do tuk

    @commands.command()
    async def sticky(self, ctx, *, message: str):
        """Активира sticky съобщение в канала"""
        channel_id = ctx.channel.id

        # Ако има старо sticky съобщение в канала - изтриваме го
        if channel_id in self.sticky:
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass

        # Пращаме новото sticky съобщение
        sticky_msg = await ctx.send(f"**Sticky:** {message}")
        self.sticky[channel_id] = {"text": message, "message": sticky_msg}

        await ctx.send(f"Sticky съобщението е настроено.")

    @commands.command()
    async def unsticky(self, ctx):
        """Деактивира sticky съобщението в този канал"""
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
        # Пропускаме съобщения от бота
        if message.author.bot:
            return

        channel_id = message.channel.id
        if channel_id in self.sticky:
            # Изтриваме старото sticky съобщение
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass

            # Пращаме отново sticky съобщението под новото съобщение
            sticky_msg = await message.channel.send(f"**Sticky:** {self.sticky[channel_id]['text']}")
            # Обновяваме референцията
            self.sticky[channel_id]["message"] = sticky_msg

async def setup(bot):
    await bot.add_cog(Sticky(bot))
