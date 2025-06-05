# Matches Cog

from discord.ext import commands
import discord
import aiosqlite
import aiohttp
from config import config  # Импортираме конфигурацията

class Match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.args = [1, 2]
        self.args_english = "1 or 2"
        self.name = "Match History"
        self.msg = "**Example**: `s!matches obsidian_mb 5`"
        self.url = config.get("match_history_api_url", "https://api.survev.io/api/match_history")  # Използваме стойността от конфигурацията
        self.headers = {"content-type": "application/json; charset=UTF-8"}

    async def check_valid_players(self, player: str):
        url = "https://api.survev.io/api/user_stats"
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = {"slug": f"{player}", "interval": "all", "mapIdFilter": "-1"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as r:
                    c = await r.json()
        except Exception as e:
            print(f"Connection Error: {e}")
            return False
        return bool(c)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Match History Cog Loaded")

    @commands.command(aliases=["matches", "match_history"])
    async def match(self, ctx):
        guild_id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        db_cursor = await conn.cursor()
        await db_cursor.execute("select prefix from servers where name = ?", [str(guild_id)])
        prefix_result = await db_cursor.fetchall()
        prefix = prefix_result[0][0]

        args = ctx.message.content.split()
        arg_count = len(args) - 1
        msg = (
            f"**Argument #1**: Player Name \n"
            f"**Argument #2** (optional): Amount of matches to return \n"
            f"**Example**: `{prefix}match obsidian_mb 5` (last 5 games of obsidian_mb)\n"
            f"**NOTE**: You must put in the **user's account name** which might differ with their in game name."
        )
        if arg_count not in self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args_english}**\n{msg}"
            )
            await conn.close()
            return

        player_name = args[1]
        last_ngames = int(args[2]) if len(args) > 2 else 10

        if last_ngames < 0:
            await ctx.send("I can't retrieve a negative amount of games")
            await conn.close()
            return

        lowered = player_name.lower()
        offset = ((last_ngames - 1) // 10) * 10
        previous_offsets = [i for i in range(0, offset) if not i % 10]

        data = {
            "slug": lowered,
            "offset": offset,
            "count": last_ngames - offset,
            "teamModeFilter": 7,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=self.headers, json=data) as r:
                    json_response = await r.json()
        except Exception as e:
            await ctx.send(
                "Connection Error. Please log an **issue description** of this with the **issue command**."
            )
            await conn.close()
            return

        valid_player = await self.check_valid_players(lowered)
        if not valid_player:
            embed = discord.Embed(
                description=f"**{player_name}** is not a valid player of survev.io.",
                color=0x00B037,
            )
            await ctx.send(embed=embed)
            await conn.close()
            return

        if json_response == []:
            desc = f"**{player_name}** doesn't have any recent games"
            embed = discord.Embed(description=desc, color=0x00B037)
            await ctx.send(embed=embed)
            await conn.close()
            return

        modes = ["Solo", "Duos", "Squads"]
        title = f"{player_name}'s Last __{last_ngames}__ games"
        embed = discord.Embed(title=title, color=0x00B037)

        for i, game in enumerate(json_response, 1):
            if not isinstance(game, dict):
                continue

            try:
                team_mode = modes[game.get("team_mode", 0) - 1]
            except (IndexError, KeyError):
                team_mode = "Unknown"

            time_alive = divmod(int(game.get("time_alive", 0)), 60)
            rank = game.get("rank", "N/A")
            kills = game.get("kills", "N/A")

            game_info = (
                f"**Mode**: {team_mode}\n"
                f"**Time Alive**: {time_alive[0]}m {time_alive[1]}s\n"
                f"**Rank**: {rank} | **Kills**: {kills}"
            )

            embed.add_field(name=f"Game #{i}", value=game_info, inline=False)

        await ctx.send(embed=embed)
        await conn.close()


async def setup(bot):
    await bot.add_cog(Match(bot))
