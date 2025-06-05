# Melee Cog

import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as soupify
import aiosqlite


class Melee(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.args = 1
        self.msg = "**Example**: `s!melee katana`"
        self.url = "https://survivio.fandom.com/wiki/Melee_Weapons"
        self.name = "Melee"

    @commands.Cog.listener()
    async def on_ready(self):
        print("Melee Cog Loaded")

    @commands.command()
    async def melee(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        msg = f"**Example**: `{prefix}melee katana`"
        if arg_count != self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args}** \n{msg}"
            )
        else:
            weapon = args[1]
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as r:
                    unparsed = await r.read()
            wep_finder = soupify(unparsed, "html.parser")
            weapons_html = wep_finder.find("table", {"class": "article-table"})
            print(weapons_html)
            wep2 = weapons_html.find_all("tr")
            wep3 = []
            wep_dict = {}
            for i in wep2:
                b = i.find_all("a")
                if len(b) > 0:
                    wep_dict[i.find_all("a")[0].text] = i.find_all("a")[1]["href"]
                    wep3.append(i.find_all("a")[0])
            in_list = False
            for i in wep_dict.keys():
                plac = i.lower()
                plac1 = weapon.lower()
                if plac == plac1:
                    act_weapon = i
                    in_list = True
                else:
                    continue
            if in_list:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://survivio.fandom.com/wiki/" + act_weapon
                    ) as r:
                        unparsed = await r.read()
                html = soupify(unparsed, "html.parser")
                equip_speed = html.find("div", {"data-source": "equipSpeed"}).text
                damage = html.find("div", {"data-source": "damage"}).text
                rad = html.find("div", {"data-source": "rad"}).text
                cltime = html.find("div", {"data-source": "cooldownTime"}).text
                auto = html.find("div", {"data-source": "autoAttack"}).text
                embed = discord.Embed(
                    title=f"{act_weapon} Stats",
                    description=f"**Damage**: {damage} \n **Attack Radius**: {rad} \n **Equip Speed**: {equip_speed} \n **Cooldown Time**: {cltime} \n **Auto Attack**: {auto}",
                    color=0x00B037,
                )
                embed = embed = discord.Embed(
                    title=f"{act_weapon} Stats",
                    description=f"**Damage**: {damage} \n **Attack Radius**: {rad} \n **Equip Speed**: {equip_speed} \n **Cooldown Time**: {cltime} \n **Auto Attack**: {auto} \n",
                    color=0x00B037,
                )
                await ctx.send(embed=embed)

            else:
                # ', '.join() is much better
                # I'll fix it later
                big_concat = ""
                for i in wep_dict.keys():
                    if big_concat == "":
                        big_concat += i
                    else:
                        place = ", " + i
                        big_concat += place
                        embed = discord.Embed(
                            description=f'**"{weapon}"** is not a valid weapon in **survev.io**. \n \n  **Valid Weapons**: '
                            + big_concat,
                            color=0x00B037,
                        )
                await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Melee(bot))
