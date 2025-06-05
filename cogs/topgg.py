import aiohttp
from discord.ext import commands, tasks

class TopGG(commands.Cog):
    def __init__(self, bot, token):
        self.bot = bot
        self.token = token
        self.post_guild_count.start()

    @tasks.loop(minutes=30)
    async def post_guild_count(self):
        url = "https://top.gg/api/bots/{}/stats".format(self.bot.user.id)
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        payload = {
            "server_count": len(self.bot.guilds)
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    print("Server count posted successfully")
                else:
                    print(f"Failed to post server count: {resp.status}")

    @post_guild_count.before_loop
    async def before_post(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    token = "YOUR_TOPGG_TOKEN"  # или зареди от файл/околна среда
    await bot.add_cog(TopGG(bot, token))
