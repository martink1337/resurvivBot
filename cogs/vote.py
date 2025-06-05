# Voting Cog
# STATUS: done

import discord
from discord.ext import commands
import json
import aiosqlite


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.args = 0
        self.name = "Voting"

    @commands.Cog.listener()
    async def on_ready(self):
        print("Voting Cog Loaded")

    @commands.command()
    async def vote(self, ctx):
        args = ctx.message.content.split()
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        msg = f"**Usage**: `{prefix}vote`"
        arg_count = len(args) - 1
        if arg_count != self.args:
            await ctx.send(
                f"**{self.name}** command only takes an argument count of **{self.args}**\n{msg}"
            )
        else:
            print("Exec")
            with open("cogs/votes.json", "r") as f:
                json_votes = json.load(f)
            votes = json_votes["votes"]
            voters = json_votes["voters"]
            print(votes)
            print(voters)
            if ctx.message.author.id not in voters:
                votes += 1
                voters.append(ctx.message.author.id)
                outline = {"votes": votes, "voters": voters}
                with open("cogs/votes.json", "w") as f:
                    json.dump(outline, f)
                desc = f"Your vote has been added. Current Vote **Count**: `{votes}`"
                await ctx.send(embed=discord.Embed(description=desc, color=0x00B037))
            else:
                desc = f"You **already** voted. Current Vote **Count**: `{votes}`"
                await ctx.send(embed=discord.Embed(description=desc, color=0x00B037))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetvotes(self, ctx):
        with open("cogs/votes.json", "w") as f:
            json.dump({"votes": 0, "voters": []}, f)
        await ctx.send(embed=discord.Embed(
            description="✅ Всички гласове бяха **нулирани**.",
            color=0x00B037
        ))


async def setup(bot):
    await bot.add_cog(Vote(bot))
