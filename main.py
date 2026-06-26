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

starred_messages = set()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def get_star_count(message: discord.Message) -> int:
    for reaction in message.reactions:
        if str(reaction.emoji) == "⭐":
            return reaction.count
    return 0

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

        star_count = await get_star_count(message)

        if star_count >= STAR_THRESHOLD and message.id not in starred_messages:
            starboard_channel = guild.get_channel(STARBOARD_CHANNEL_ID)

            if starboard_channel is None:
                return

            embed = discord.Embed(
                description=message.content or "*No text content*",
                color=discord.Color.gold()
            )

            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url
            )

            embed.add_field(
                name="Jump to Message",
                value=f"[Click here]({message.jump_url})",
                inline=False
            )

            embed.set_footer(text=f"⭐ {star_count} | #{message.channel.name}")

            if message.attachments:
                embed.set_image(url=message.attachments[0].url)

            await starboard_channel.send(embed=embed)

            starred_messages.add(message.id)

    except Exception as e:
        print(f"Error handling reaction: {e}")

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    pass

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
