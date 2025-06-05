import discord
from discord.ext import commands
import aiosqlite


class Feedback(commands.Cog):
    def __init__(self, bot):
        # Takes any number of args
        self.bot = bot
        self.admin = [220212030546771970]

    @commands.Cog.listener()
    async def on_ready(self):
        print("Feedback Cog Loaded")

    @commands.command(aliases=["fix", "problem", "issues"])
    async def issue(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        name = "Issue"
        msg = f"**Example**: `{prefix}issue NOTHING IS WORKING`"
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        if arg_count == 0:
            await ctx.send(
                f"**{name}** command only takes an argument count of **{len(args)}** \n{msg}"
            )
        else:
            issue = " ".join(args[1:])
            conn2 = await aiosqlite.connect("issues.db")
            c2 = await conn2.cursor()
            await c2.execute(
                """create table if not exists issues(
                    id integer primary key autoincrement,
                    issue text
                    )"""
            )
            await conn2.commit()
            await c2.execute("insert into issues (issue) values (?)", [issue])
            await conn2.commit()
            await c2.execute("SELECT MAX(ID) FROM ISSUES")
            d = await c2.fetchall()
            d = d[0][0]
            embed = discord.Embed(
                description=f"**Issue #{d}** Registered: '**{issue}**'", color=0x00B037
            )
            await ctx.send(embed=embed)
            await conn2.close()
        await conn.close()

    @commands.command(aliases=["suggestion", "addition", "suggest"])
    async def sug(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        name = "Suggestion"
        msg = f"**Example**: `{prefix}suggest twitch add more commands!`"
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        if arg_count == 0:
            await ctx.send(
                f"**{name}** command only takes an argument count of **{len(args)}** \n{msg}"
            )
        else:
            suggestion = " ".join(args[1:])
            conn2 = await aiosqlite.connect("suggestions.db")
            c2 = await conn2.cursor()
            await c2.execute(
                """create table if not exists suggestions(
                    id integer primary key autoincrement,
                    suggestion text
                    )"""
            )
            await conn2.commit()
            await c2.execute(
                "insert into suggestions (suggestion) values (?)", [suggestion]
            )
            await conn2.commit()
            await c2.execute("SELECT MAX(ID) FROM SUGGESTIONS")
            d = await c2.fetchall()
            d = d[0][0]
            embed = discord.Embed(
                description=f"**Suggestion #{d}** Registered: '**{suggestion}**'",
                color=0x00B037,
            )
            await ctx.send(embed=embed)
            await conn2.close()
        await conn.close()

    @commands.command(aliases=["fetchsugs"])
    async def fetchs(self, ctx):
        author = ctx.message.author.id
        if author in self.admin:
            conn = await aiosqlite.connect("suggestions.db")
            c = await conn.cursor()
            # Създаваме таблицата, ако я няма
            await c.execute(
                """CREATE TABLE IF NOT EXISTS suggestions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion TEXT
                )"""
            )
            await conn.commit()

            b = await c.execute("SELECT * FROM suggestions")
            b = await b.fetchall()
            if not b:
                await ctx.send("Все още няма добавени предложения.")
                await conn.close()
                return

            concat = ""
            for r in b:
                if concat != "":
                    concat += f"\n{r[1]}"
                else:
                    concat += f"{r[1]}"

            embed = discord.Embed(
                title="**Suggestions**", description=concat, color=0x00B037
            )
            user = await self.bot.fetch_user(author)
            if user is None:
                await ctx.send("Не мога да намеря вашия Discord акаунт за да изпратя лично съобщение.")
                await conn.close()
                return
            try:
                await user.send(embed=embed, delete_after=3600)
                await ctx.message.add_reaction("✅")
            except discord.Forbidden:
                await ctx.send("Не мога да ти изпратя лично съобщение. Моля, провери настройките си за поверителност.")
            await conn.close()
        else:
            await ctx.send(
                "You checked the code repo. Good for you, but you can't run this command unless you contribute to the bot"
            )

    @commands.command(aliases=["fetchissues", "fetchis", "fetchissue"])
    async def fetchi(self, ctx):
        author = ctx.message.author.id
        if author in self.admin:
            conn = await aiosqlite.connect("issues.db")
            c = await conn.cursor()
            # Създаваме таблицата, ако я няма
            await c.execute(
                """CREATE TABLE IF NOT EXISTS issues(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue TEXT
                )"""
            )
            await conn.commit()

            b = await c.execute("SELECT * FROM issues")
            b = await b.fetchall()
            if not b:
                await ctx.send("Все още няма добавени проблеми.")
                await conn.close()
                return

            concat = ""
            for r in b:
                if concat != "":
                    concat += f"\n{r[1]}"
                else:
                    concat += f"{r[1]}"

            embed = discord.Embed(
                title="**Issues**", description=concat, color=0x00B037
            )
            user = await self.bot.fetch_user(author)
            if user is None:
                await ctx.send("Не мога да намеря вашия Discord акаунт за да изпратя лично съобщение.")
                await conn.close()
                return
            try:
                await user.send(embed=embed, delete_after=3600)
                await ctx.message.add_reaction("✅")
            except discord.Forbidden:
                await ctx.send("Не мога да ти изпратя лично съобщение. Моля, провери настройките си за поверителност.")
            await conn.close()
        else:
            await ctx.send(
                "You checked the code repo. Good for you, but you can't run this command unless you contribute to the bot"
            )


async def setup(bot):
    await bot.add_cog(Feedback(bot))
