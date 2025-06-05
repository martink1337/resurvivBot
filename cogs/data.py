# Data Alteration Cog
# STATUS: config command

import discord
from discord.ext import commands
import aiosqlite
from config import config

class Data(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles = config.get("privileged_roles", [])

    @commands.Cog.listener()
    async def on_ready(self):
        print("Data Cog Loaded")

    @commands.command(aliases=["change_prefix", "prefix"])
    async def change_pref(self, ctx):
        id = ctx.message.guild.id
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(id)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        arg_limit = 1
        args = ctx.message.content.split()
        arg_count = len(args) - 1
        server = ctx.message.guild
        vals = []
        server = ctx.message.guild
        name = ctx.message.guild.id
        for member in server.members:
            for role in member.roles:
                if role.name.lower() in self.roles:
                    vals.append(member.id)
        print(name)
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("select prefix from servers where name = ?", [str(name)])
        prefix = await c.fetchall()
        prefix = prefix[0][0]
        print(prefix)
        com_name = "Change Prefix"
        msg = f"**Argument #1**: New Prefix \n**Example**: `{prefix}change_pref #`\n**NOTE**: Prefixes should not contain spaces"
        if arg_count != arg_limit:
            await ctx.send(
                f"**{com_name}** command only takes an argument count of **{arg_limit}** \n{msg}"
            )
        else:
            if ctx.message.author.id in vals:
                new_pref = args[1]
                print(new_pref)
                print(ctx.message.author.name)
                if prefix == new_pref:
                    embed = discord.Embed(
                        description=f"`{prefix}` is already the **current prefix**",
                        color=0x00B037,
                    )
                    await ctx.send(embed=embed)
                await c.execute(
                    "update servers set prefix = ? where name = ?",
                    [str(new_pref), str(name)],
                )
                await conn.commit()
                await c.execute(
                    "update servers set changer = ? where name = ?",
                    [str(ctx.message.author.name), str(name)],
                )
                await conn.commit()
                print(name)
                await c.execute(
                    "select prefix from servers where name = ?", [str(name)]
                )
                embed = discord.Embed(
                    description=f"Prefix has successfully been changed from **{prefix}** to **{new_pref}** by **{ctx.message.author.name}**",
                    color=0x00B037,
                )
                await ctx.send(embed=embed)
            else:
                prefix = await self.bot.command_prefix(self.bot, ctx.message)
                help_form = prefix + "help"
                embed = discord.Embed(
                    description=f"**{ctx.message.author.name}** you do not have permission to use this command \n Type `{help_form}` for more",
                    color=0x00B037,
                )
                await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Data(bot))
