import discord
from discord.ext import commands
from config import config  # We import the configuration

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
        """Enables sticky messages in the channel"""

        user_roles = [r.name.lower() for r in ctx.author.roles]
        if not any(role in user_roles for role in self.staff_roles):
            await ctx.send("You do not have the necessary permissions to use this command.")
            return

        channel_id = ctx.channel.id

        if channel_id in self.sticky:
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass

        sticky_msg = await ctx.send(f"**Sticky:** {message}")
        self.sticky[channel_id] = {"text": message, "message": sticky_msg}
        await ctx.send("Sticky message is set.")

    @commands.command()
    async def unsticky(self, ctx):
        """Disables sticky messages in this channel"""

        user_roles = [r.name.lower() for r in ctx.author.roles]
        if not any(role in user_roles for role in self.staff_roles):
            await ctx.send("You do not have the necessary permissions to use this command.")
            return

        channel_id = ctx.channel.id
        if channel_id in self.sticky:
            try:
                await self.sticky[channel_id]["message"].delete()
            except:
                pass
            del self.sticky[channel_id]
            await ctx.send("Sticky disabled in this channel.")
        else:
            await ctx.send("There is no active sticky in this channel.")

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

            sticky_msg = await message.channel.send(f"**STICKY:** {self.sticky[channel_id]['text']}")
            self.sticky[channel_id]["message"] = sticky_msg

async def setup(bot):
    await bot.add_cog(Sticky(bot))
