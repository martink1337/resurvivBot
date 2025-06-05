import asyncio
import os
import discord
from discord.ext import commands
from config import config

TICKET_CATEGORY_ID = config.get("ticket_category_id")
TRANSCRIPTS_CHANNEL_ID = config.get("transcripts_channel_id")

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.panel_channel_id = None
        self.panel_message_id = None

    async def _check_inactivity(self, channel, member, first_wait=300, second_wait=300):
        """Проверява дали member е писал в channel, ако не - предупреждава, ако пак не - затваря."""
        await asyncio.sleep(first_wait)  # първи таймаут - 5 минути

        messages = [msg async for msg in channel.history(limit=50, oldest_first=True)]
        has_written = any(msg.author.id == member.id for msg in messages)

        if not has_written:
            try:
                await channel.send(f"{member.mention}, здравей! Ако не напишеш нищо, твоя тикет ще бъде затворен след 5 минути!")
            except Exception as e:
                print(f"Не успях да изпратя предупреждение: {e}")

            await asyncio.sleep(second_wait)  # втори таймаут - още 5 минути

            messages = [msg async for msg in channel.history(limit=50, oldest_first=True)]
            has_written = any(msg.author.id == member.id for msg in messages)

            if not has_written:
                try:
                    # Запиши транскрипта преди да изтриеш канала
                    transcript = ""
                    for msg in messages:
                        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                        transcript += f"[{timestamp}] {msg.author.name}: {msg.content}\n"

                    filename = f"transcript-{channel.name}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(transcript)

                    transcripts_channel = channel.guild.get_channel(TRANSCRIPTS_CHANNEL_ID)
                    if transcripts_channel:
                        await transcripts_channel.send(file=discord.File(filename))

                    os.remove(filename)
                except Exception as e:
                    print(f"Грешка при създаване на транскрипта: {e}")

                await channel.delete()
        else:
            # Ако потребителят е писал, не правим нищо
            return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(
            title="Тикет панел",
            description="Реагирай с 🎫 за да отвориш тикет.",
            color=discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎫")
        self.panel_message_id = msg.id
        self.panel_channel_id = msg.channel.id

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id == self.panel_message_id and payload.channel_id == self.panel_channel_id:
            if str(payload.emoji) == "🎫":
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                if member.bot:
                    return

                category = guild.get_channel(TICKET_CATEGORY_ID)
                if category is None or not isinstance(category, discord.CategoryChannel):
                    category = await guild.create_category("tickets")

                existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
                if existing:
                    try:
                        await member.send("Вече имаш отворен тикет!")
                    except:
                        pass
                    panel_channel = self.bot.get_channel(payload.channel_id)
                    if panel_channel:
                        message = await panel_channel.fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji, member)
                    return

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                }
                channel = await guild.create_text_channel(
                    f"ticket-{member.name.lower()}", category=category, overwrites=overwrites
                )

                embed = discord.Embed(
                    title="Тикет",
                    description=f"Здравей {member.mention}! Реагирай с 🔒 за да затвориш тикета си.",
                    color=discord.Color.red()
                )
                ticket_msg = await channel.send(embed=embed)
                await ticket_msg.add_reaction("🔒")

                # Стартираме проверката за активност с автоматично затваряне
                asyncio.create_task(self._check_inactivity(channel, member))

                # Премахване на реакцията от панела
                panel_channel = self.bot.get_channel(payload.channel_id)
                if panel_channel:
                    try:
                        message = await panel_channel.fetch_message(payload.message_id)
                        await message.remove_reaction(payload.emoji, member)
                    except:
                        pass

        elif str(payload.emoji) == "🔒":
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)

            if channel and channel.name.startswith("ticket-"):
                messages = [msg async for msg in channel.history(limit=None, oldest_first=True)]
                transcript = ""
                for msg in messages:
                    timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                    transcript += f"[{timestamp}] {msg.author.name}: {msg.content}\n"

                filename = f"transcript-{channel.name}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(transcript)

                transcripts_channel = guild.get_channel(TRANSCRIPTS_CHANNEL_ID)
                if transcripts_channel:
                    await transcripts_channel.send(file=discord.File(filename))

                try:
                    os.remove(filename)
                except:
                    pass

                await channel.delete()

async def setup(bot):
    await bot.add_cog(Ticket(bot))
