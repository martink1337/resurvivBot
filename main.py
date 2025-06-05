import discord
from discord.ext import commands
import os
import aiosqlite
import nest_asyncio

# Импортираш config от config.py
from config import config

# temporary disabled because in windows terminal it freezes
nest_asyncio.apply()

token = config["bot_token"]  # Вземаш token от config

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

async def get_pref(bot, msg):
    name = msg.guild.id
    conn = await aiosqlite.connect("servers.db")
    c = await conn.cursor()
    await c.execute("select prefix from servers where name = ?", [str(name)])
    cor_fetch = await c.fetchall()
    prefix = cor_fetch[0][0]
    return prefix

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_pref, intents=intents)

    async def setup_hook(self):
        dont_load = ["playerutils.py"]
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and file not in dont_load:
                await self.load_extension(f"cogs.{file[:-3]}")

    async def on_ready(self):
        print("Bot Is Running ...")
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute(
            """CREATE TABLE IF NOT EXISTS SERVERS(
                    NAME TEXT,
                    CHANGER TEXT,
                    PREFIX TEXT,
                    CONFIG TEXT,
                    CHANGER2 TEXT,
                    GEN BOOL
            )"""
        )
        await conn.commit()

        current_servers = [str(server.id) for server in self.guilds]
        print(f"Bot is Running on {len(current_servers)}!")
        await c.execute("select name from servers")
        d = await c.fetchall()
        e = [i[0] for i in d]
        print(e)

        for s in current_servers:
            if s not in e:
                await c.execute(
                    "insert into servers values (?, 'None', 's!', '', 'None', 1)", [str(s)]
                )
                await conn.commit()

        for old in e:
            if old not in current_servers:
                await c.execute("delete from servers where name = ?", [str(old)])
                await conn.commit()

        stream = discord.Streaming(
            name=f"s!help on {len(self.guilds)} servers!",
            url="https://www.twitch.tv/survivstatbot",
        )
        await self.change_presence(activity=stream)

    async def on_guild_join(self, guild):
        print(f"Bot was added to {guild} :)")
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute(
            "insert into servers values (?, 'None', 's!', '', 'None', 1)", [str(guild.id)]
        )
        await conn.commit()

    async def on_guild_remove(self, guild):
        print(f"Bot was removed from {guild} :(")
        conn = await aiosqlite.connect("servers.db")
        c = await conn.cursor()
        await c.execute("delete from servers where name = ?", [str(guild.id)])
        await conn.commit()

bot = MyBot()
bot.run(token)
