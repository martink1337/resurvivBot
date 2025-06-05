# Help Cog
# STATUS:
# add a feature to look deep into an indivual's command help


import discord
from discord.ext import commands
import json


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help Cog Loaded")

    @commands.command(aliases=["info", "support"])
    async def help(self, ctx):
        prefix = await self.bot.command_prefix(self.bot, ctx.message)
        is_form = prefix + "issue "
        sug_form = prefix + "suggest "
        gun_form = prefix + "gun "
        play_form = prefix + "player "
        help_form = prefix + "help"
        ping_form = prefix + "ping"
        up_form = prefix + "update"
        mel_form = prefix + "melee "
        change_form = prefix + "change_pref "
        config_form = prefix + "config "
        twitch_form = prefix + "twitch"
        link_gen_form = prefix + "link_gen"
        vote_form = prefix + "vote"
        with open("cogs/votes.json", "r") as f:
            json_votes = json.load(f)
        vote_count = json_votes["votes"]
        embed = discord.Embed(
            title=f" Current Servers: `{len(self.bot.guilds)}`\n\U0001f44d Using the Surviv Stats Bot \U0001f44d",
            description=f"\U0001F52B `{gun_form}(gun_name)`: **Gets the Stats of a Gun** *notice the space \n ℹ️`{play_form}(player)`: **Getting Stats of Player** *notice the space \n \U0001F3D3 `{ping_form}`: **Check the Latency of Surviv Stat Bot** \n ⏫ `{up_form}`: **Get the current update in survev.io** \n 🔪 `{mel_form}(melee)`: **Get the Stats of the Melee Weapon** \n 📖 `{is_form}(text)`: **Log in issue in surviv stat bot that we will try to fix** \n 📝 `{sug_form}(text)`: **Suggest a feature for the bot** \n 👀 `{twitch_form}`: **Gets Current Twitch Streamers** \n 🗳️ `{vote_form}`: **Cast your vote that you like the bot.** Vote Count: `{vote_count}` \n 🤔 `{change_form}(prefix)`: **Changes Prefix from `{prefix}` to something else.** \n  NOTE: Only server members with roles: **Owner, Moderator, Manager, or Admin** are allowed to use the **Change Prefix** Command.",
            color=0x00B037,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    # Removing existing help command
    # in place of new one
    bot.remove_command("help")
    await bot.add_cog(Help(bot))
