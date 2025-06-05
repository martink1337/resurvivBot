# Latency Cog
# Status: done

import discord
from discord.ext import commands
import aiosqlite


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.args = 0
        self.msg = "**Example**: `s!ping`"
        self.name = "Ping"

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping Cog Loaded")

    @commands.command()
    async def ping(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        args = ctx.message.content.split()
        msg = f"**Example**: `{prefix}ping`"
        arg_count = len(args) - 1
        if arg_count != self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args}** \n{msg}"
            )
        else:
            ping = str(round(self.bot.latency, 3))
            embedping = discord.Embed(
                title="\U0001F3D3 Pong! \U0001F3D3",
                description=f"**Checking Stats** at a **latency** of **{ping} ms**",
                color=0x00B037,
            )
            await ctx.send(embed=embedping)


async def setup(bot):
    await bot.add_cog(Ping(bot))
