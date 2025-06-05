# Update Cog
# STATUS: done

import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as soupify
import aiosqlite
import sys

# Настройваме stdout за UTF-8, за да не дава грешки при print на емоджита
sys.stdout.reconfigure(encoding='utf-8')

class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Update"
        self.args = 0
        self.url = "http://survev.io/"
        self.msg = "**Example**: `s!update`"

    @commands.Cog.listener()
    async def on_ready(self):
        print("Update Cog Loaded")

    @commands.command(aliases=["releases", "release", "updates", "new"])
    async def update(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        msg = f"**Example**: `{prefix}update`"
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        if arg_count != self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args}** \n{msg}"
            )
        else:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url) as r:
                        raw = await r.read()
            except Exception:
                await ctx.send(
                    "Failed to connect to survev.io website. Log an issue with the issue command"
                )
                return  # спираме, ако има грешка

            html = soupify(raw, "html.parser")
            news_wrapper = html.find("div", {"id": "news-current"})

            if not news_wrapper:
                await ctx.send("Could not find the latest update news on the site.")
                return

            date = news_wrapper.find("small").text
            title = news_wrapper.find("strong").text
            title = f"⏫ {title} ({date}) ⏫"
            desc = news_wrapper.findAll("p")[1].text

            # Принтираме безопасно в конзолата
            print(title.encode('utf-8', errors='ignore').decode('utf-8'))
            print(desc.encode('utf-8', errors='ignore').decode('utf-8'))

            embed = discord.Embed(title=title, description=desc, color=0x00B037)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Update(bot))
