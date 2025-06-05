# Twitch Cog
# STATUS: done

import discord
from discord.ext import commands
import aiohttp
import aiosqlite


class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.headers = {"content-type": "application/json; charset=utf-8"}
        self.url = "https://survev.io/api/site_info?language=en"
        self.title = "Current Twitch Streamers"
        self.args = 0
        self.name = "Twitch"
        self.msg = "**Example**: `s!twitch`"

    @commands.Cog.listener()
    async def on_ready(self):
        print("Twitch Cog Loaded")

    @commands.command(aliases=["streamers"])
    async def twitch(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        msg = f"**Example**: `{prefix}twitch`"
        if arg_count != self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args}** \n{msg}"
            )

        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url, headers=self.headers) as r:
                    if r.status == 200:
                        json = await r.json()
                        dict = {}
                        for i in json["twitch"]:
                            dict[i["name"]] = i["url"], i["viewers"]
                        b = ""
                        d = list(dict.keys())
                        for i in range(len(d)):
                            if i == 0:
                                b += f'**{d[0]}**: ["Watch!"]({dict[d[0]][0]}), Viewers: `{dict[d[0]][1]}` \n '
                            else:
                                b += f'**{d[i]}**: ["Watch!"]({dict[d[i]][0]}), Viewers: `{dict[d[i]][1]}` \n '
                        main = b
                        embed = discord.Embed(
                            title="Current Twitch Streamers",
                            description=main,
                            color=0x00B037,
                        )
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(
                            "Bad Web Request to the survev.io API. Log an issue with the issue command"
                        )


async def setup(bot):
    await bot.add_cog(Twitch(bot))
