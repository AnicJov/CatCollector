import discord
from discord.ext import commands
import sqlite3
import secrets
import string
import time
import os
from dotenv import load_dotenv


# Connect to the SQLite database that stores cat collections.
conn = sqlite3.connect("cat_collection.db")
c = conn.cursor()

# Create a table for linking Discord accounts to Twitch usernames.
c.execute(
    """CREATE TABLE IF NOT EXISTS links (
         discord_id TEXT PRIMARY KEY,
         twitch_username TEXT
    )"""
)
c.execute("""CREATE TABLE IF NOT EXISTS link_requests (
                discord_user_id INTEGER PRIMARY KEY,
                code TEXT NOT NULL,
                expires_at REAL NOT NULL
            )""")
conn.commit()

load_dotenv()


def generate_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def get_user_collection(twitch_username):
    """Retrieve the cat collection for the given Twitch username."""
    c.execute("SELECT cats FROM collections WHERE user=?", (twitch_username,))
    row = c.fetchone()
    if row:
        return row[0].split()
    return []

def link_account(discord_id, twitch_username):
    """Link a Discord ID with a Twitch username."""
    c.execute("INSERT OR REPLACE INTO links (discord_id, twitch_username) VALUES (?, ?)", (discord_id, twitch_username))
    conn.commit()

def get_linked_twitch(discord_id):
    """Get the linked Twitch username for the given Discord ID, if any."""
    c.execute("SELECT twitch_username FROM links WHERE discord_id=?", (discord_id,))
    row = c.fetchone()
    if row:
        return row[0]
    return None

# A dictionary mapping cat emote codes to the Discord application's custom emoji IDs.
CAT_EMOTES = {
    "zuh": "1339043502138462300",
    "yuh": "1339043435876716595",
    "xuh": "1339043363583823922",
    "wuh": "1339043290653265920",
    "vuh": "1339043156452184104",
    "uuh": "1339043001644744824",
    "tuh": "1339042946649034752",
    "suh": "1339042891170844734",
    "ruh": "1339042828323389471",
    "quh": "1339042749814411356",
    "puh": "1339042621594538047",
    "ouh": "1339042570189275156",
    "nuh": "1339042498374402066",
    "muh": "1339042434239430768",
    "luh": "1339042360964812852",
    "kuh": "1339042265988857866",
    "juh": "1339042119545000028",
    "iuh": "1339041995145871401",
    "huh": "1339041905907994664",
    "guh": "1339041816170856528",
    "fuh": "1339041576600731690",
    "euh": "1339041408820056085",
    "duh": "1339041332844298291",
    "buh": "1339040988785545276",
    "cuh": "1339036496421715998",
    "auh": "1339036432664105068"
}

def get_cat_emoji(cat_code):
    """
    Return the formatted custom emoji string for a given cat code.
    The format for custom emojis is: <a:name:id>
    """
    if cat_code in CAT_EMOTES.keys():
        return f"<a:{cat_code}:{CAT_EMOTES[cat_code]}>"
    return cat_code  # fallback to the text code if not found


# Set up the bot with the required intents.
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

    channels_to_announce_to = os.getenv("DISCORD_CHANNELS_ANNOUNCE").split(',')

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name in channels_to_announce_to:
                await channel.send(os.getenv("DISCORD_JOIN_MESSAGE"))
                break


@bot.command(name="link")
async def link(ctx):
    """
    Sends DM with a code to link Discord account to Twitch account.
    """
    code = generate_code()
    discord_user_id = ctx.author.id
    expires_at = time.time() + int(os.getenv('LINK_CODE_EXPIRATION'))

    # Store the code and expiration time in the database
    c.execute("INSERT OR REPLACE INTO link_requests (discord_user_id, code, expires_at) VALUES (?, ?, ?)",
              (discord_user_id, code, expires_at))
    conn.commit()

    try:
        # FIXME: This should say the actual configured time instead of the default 10 minutes
        await ctx.author.send(f"Your linking code is: `{code}`\nIt will expire in 10 minutes.\nGo to Twitch chat and type `!link {code}` to complete the linking\n:3")
        await ctx.send("A linking code has been sent to your DMs :3")
    except discord.Forbidden:
        await ctx.send("I couldn't send you a DM. Please check your privacy settings.")


@bot.command(name="collection")
async def collection(ctx, member: discord.Member = None):
    """
    Show a user's cat collection.
    
    If no member is specified, it shows the collection for the command invoker.
    The bot looks up the user's Twitch username from the linked accounts table
    and then reads their cat collection from the database.
    
    For each cat code (like 'fuh'), the bot uses the CAT_EMOTES dictionary to convert
    it to a custom emoji string (in the format <a:{name}:{id}>).
    """
    if member is None:
        member = ctx.author

    twitch_username = get_linked_twitch(str(member.id))
    if twitch_username is None:
        await ctx.send(f"{member.mention} has not linked their Twitch account. Use `!link` to link your account.")
        return

    cat_codes = get_user_collection(twitch_username)
    if not cat_codes:
        await ctx.send(f"{member.mention}, you haven't caught any kitties yet!")
        return

    cat_emojis = [get_cat_emoji(code) for code in cat_codes]
    await ctx.send(f"{member.mention}'s cat collection: {' '.join(cat_emojis)}")


bot.run(os.getenv("DISCORD_TOKEN"))
