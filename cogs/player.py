import discord
from discord.ext import commands
import aiohttp
import aiosqlite
from config import config  # Импортираме конфигурацията

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = config.get("user_stats_api_url", "https://api.survev.io/api/user_stats")  # Използваме стойността от конфигурацията
        self.headers = {"content-type": "application/json; charset=UTF-8"}
        self.name = "Player"
        self.msg = "**Argument #1**: Player Name \n**Example**: `s!player obsidian_mb`\n**NOTE**: You must put in the **user's account name** which might differ with their in game name."
        self.args = 1

    @commands.Cog.listener()
    async def on_ready(self):
        print("Player Cog Loaded")

    @commands.command(aliases=["players", "user", "users"])
    async def player(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        msg = f"**Argument #1**: Player Name \n**Example**: `{prefix}player obsidian_mb`\n**NOTE**: You must put in the **user's account name** which might differ with their in game name."
        if arg_count != self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args}**\n{msg}"
            )
            return  # важно да спрем тук

        player_name = args[1]
        b = player_name.lower()
        data = {"slug": b, "interval": "all", "mapIdFilter": "-1"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=self.headers, json=data) as r:
                    if r.status != 200:
                        await ctx.send(f"API returned status code {r.status}")
                        return
                    c = await r.json()
        except Exception as e:
            await ctx.send(
                f"Connection Error: {e}. Please log an **issue description** with the **issue command**."
            )
            return

        # Проверка дали има валидни данни (примерно slug да не е празно)
        if not c or not c.get("slug"):
            embed = discord.Embed(
                description=f"**{player_name}** is not a valid player of api.survev.io.",
                color=0x00B037,
            )
            await ctx.send(embed=embed)
            return

        # Безопасно извличаме данни с .get(), задаваме 0 по подразбиране
        kills = c.get("kills", 0)
        wins = c.get("wins", 0)
        games = c.get("games", 0)
        kg = c.get("kpg", 0)
        modes = c.get("modes", [])

        # За mostKills и mostDamage правим безопасна проверка
        if modes:
            mostkills = max([i.get("mostKills", 0) for i in modes])
            maxdamage = max([i.get("mostDamage", 0) for i in modes])
        else:
            mostkills = 0
            maxdamage = 0

        embed = discord.Embed(
            title=f"**{c.get('username', player_name)}'s Stats**",
            description=(
                f"**Wins**: {wins}\n"
                f"**Kills**: {kills}\n"
                f"**Games**: {games}\n"
                f"**Kill Per Game Avg**: {kg}\n"
                f"**Max Kills**: {mostkills}\n"
                f"**Most Damage**: {maxdamage}"
            ),
            color=0x00B037,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Player(bot))
