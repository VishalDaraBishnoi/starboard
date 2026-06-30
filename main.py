import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
STARBOARD_CHANNEL_ID = int(os.getenv("STARBOARD_CHANNEL_ID"))
STAR_THRESHOLD = int(os.getenv("STAR_THRESHOLD", 3))

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

starboard_messages = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def get_star_count(message: discord.Message) -> int:
    for reaction in message.reactions:
        if str(reaction.emoji) == "⭐":
            return reaction.count
    return 0

def create_embed(message: discord.Message, star_count: int):
    embed = discord.Embed(
        description=message.content or "*No text content*",
        color=discord.Color.gold(),
        timestamp=message.created_at
    )

    embed.set_author(
        name=str(message.author),
        icon_url=message.author.display_avatar.url
    )

    embed.add_field(
        name="Source",
        value=f"[Jump]({message.jump_url})",
        inline=False
    )

    embed.set_footer(text=f"⭐ {star_count} | #{message.channel.name}")

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and "image" in attachment.content_type:
                embed.set_image(url=attachment.url)
                break

    return embed

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != "⭐":
        return

    try:
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id)
        if channel is None:
            return

        message = await channel.fetch_message(payload.message_id)

        if message.channel.id == STARBOARD_CHANNEL_ID:
            return

        if message.author.bot:
            return

        if message.author.id == payload.user_id:
            return

        star_count = await get_star_count(message)

        starboard_channel = guild.get_channel(STARBOARD_CHANNEL_ID)
        if starboard_channel is None:
            return

        if star_count >= STAR_THRESHOLD:
            embed = create_embed(message, star_count)

            if message.id in starboard_messages:
                try:
                    star_msg = await starboard_channel.fetch_message(starboard_messages[message.id])
                    await star_msg.edit(embed=embed)
                except:
                    pass
            else:
                star_msg = await starboard_channel.send(embed=embed)
                starboard_messages[message.id] = star_msg.id

            print(f"Star added: {message.id} | Count: {star_count}")

    except Exception as e:
        print(f"Error handling reaction add: {e}")

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if str(payload.emoji) != "⭐":
        return

    try:
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id)
        if channel is None:
            return

        message = await channel.fetch_message(payload.message_id)

        if message.id not in starboard_messages:
            return

        star_count = await get_star_count(message)

        starboard_channel = guild.get_channel(STARBOARD_CHANNEL_ID)
        if starboard_channel is None:
            return

        if star_count < STAR_THRESHOLD:
            try:
                star_msg = await starboard_channel.fetch_message(starboard_messages[message.id])
                await star_msg.delete()
                del starboard_messages[message.id]
            except:
                pass
        else:
            embed = create_embed(message, star_count)
            try:
                star_msg = await starboard_channel.fetch_message(starboard_messages[message.id])
                await star_msg.edit(embed=embed)
            except:
                pass

    except Exception as e:
        print(f"Error handling reaction remove: {e}")

@bot.event
async def on_command_error(ctx, error):
    print(f"Command error: {error}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN is not set in .env file.")

    bot.run(TOKEN)
