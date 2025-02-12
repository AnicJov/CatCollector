import asyncio
import random
import sqlite3
import time
import os
from twitchio.ext import commands, routines
from dotenv import load_dotenv


conn = sqlite3.connect("cat_collection.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS collections (
        user TEXT PRIMARY KEY,
        cats TEXT
    )"""
)
c.execute("""CREATE TABLE IF NOT EXISTS link_requests (
                discord_user_id INTEGER PRIMARY KEY,
                code TEXT NOT NULL,
                expires_at REAL NOT NULL
            )""")
conn.commit()

load_dotenv()

ALL_CATS = {f"{c}uh" for c in "abcdefghijklmnopqrstuvwxyz"}


class Bot(commands.Bot):
    spawn_interval = [int(x) for x in os.getenv("SPAWN_INTERVAL").split(',')]
    catch_interval = int(os.getenv("CATCH_INTERVAL"))
    join_message = os.getenv("TWITCH_JOIN_MESSAGE")

    def __init__(self):
        super().__init__(token=os.getenv("TWITCH_TOKEN"), prefix='!', initial_channels=os.getenv("CHANNELS").split(','))
        self.current_cat = None
        self.catch_window = None
        self.spawn_cat.start()

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

        if self.join_message:
            for channel in self.connected_channels:
                await channel.send(f"{self.join_message}")

    def generate_cat(self):
        """Generate a random cat emote, e.g. 'xuh', 'fuh', etc."""
        return f"{random.choice('abcdefghijklmnopqrstuvwxyz')}uh"

    @routines.routine(minutes=spawn_interval[0], wait_first=True)
    async def spawn_cat(self):
        """
        Spawns a cat in chat, sets a catch window,
        and schedules a check to announce if no one catches the cat.
        After each spawn, a new random interval is set.
        """
        self.current_cat = self.generate_cat()
        self.catch_window = time.time() + self.catch_interval  # 2-minute catch period
        cat_name = self.current_cat  # Store locally for end_catch_period check
        
        for channel in self.connected_channels:
            await channel.send(f"A kitty appeared! {self.current_cat} Use !kitty to catch it!")
        
        asyncio.create_task(self.end_catch_period(cat_name))
        
        new_interval = random.randint(self.spawn_interval[0], self.spawn_interval[1])
        self.spawn_cat.change_interval(minutes=new_interval, wait_first=True)
        print(f"Next cat spawn scheduled.")

    async def end_catch_period(self, cat_name):
        """Waits `catch_interval` seconds and, if the cat wasn't caught, announces it ran away."""
        await asyncio.sleep(self.catch_interval)
        if self.current_cat == cat_name:
            for channel in self.connected_channels:
                await channel.send(f"{cat_name} ran away...")
            self.current_cat = None

    @commands.command()
    async def kitty(self, ctx: commands.Context):
        if self.current_cat is not None and time.time() <= self.catch_window:
            user_collection = self.get_user_collection(ctx.author.name)
            if self.current_cat in user_collection:
                await ctx.send(f"{ctx.author.name} , you already caught {self.current_cat} !")
                return
            self.add_cat_to_collection(ctx.author.name, self.current_cat)
            await ctx.send(f"{ctx.author.name} caught {self.current_cat} !")
            self.current_cat = None
            self.catch_window = 0
            
            updated_collection = self.get_user_collection(ctx.author.name)
            if set(updated_collection) == ALL_CATS:
                await ctx.send(f"🎉 {ctx.author.name} has caught ALL the kitties! Congratulations! 🎉")
        else:
            await ctx.send(f"Sorry {ctx.author.name} , no kitty to catch right now!")

    @commands.command()
    async def collection(self, ctx: commands.Context):
        """Displays the user's collection of caught cats."""
        cats = self.get_user_collection(ctx.author.name)
        if cats:
            await ctx.send(f"{ctx.author.name} 's cat collection: {' '.join(cats)}")
        else:
            await ctx.send(f"{ctx.author.name} , you haven't caught any kitties yet!")

    @commands.command()
    async def link(self, ctx, code: str):
        # Retrieve the record associated with the code
        c.execute("SELECT discord_user_id, expires_at FROM link_requests WHERE code = ?", (code,))
        result = c.fetchone()

        if result:
            discord_user_id, expires_at = result
            if time.time() < expires_at:
                twitch_username = ctx.author.name
                # Store the association between discord_user_id and twitch_username
                c.execute("INSERT OR REPLACE INTO links (discord_id, twitch_username) VALUES (?, ?)",
                        (discord_user_id, twitch_username))
                conn.commit()

                await ctx.send(f"Linking successful! Discord user is now linked to Twitch user {twitch_username} .")
                # Optionally, notify the user on Discord about the successful linking
                # discord_user = await discord_bot.fetch_user(discord_user_id)
                # await discord_user.send(f"Your Discord account has been linked to Twitch user {twitch_username}.")
            else:
                await ctx.send("This code has expired. Please initiate the linking process again.")
        else:
            await ctx.send("Invalid code. Please check the code and try again.")

    def add_cat_to_collection(self, user, cat):
        c.execute("SELECT cats FROM collections WHERE user=?", (user,))
        row = c.fetchone()
        if row:
            cats = row[0].split()
            if cat not in cats:
                cats.append(cat)
            c.execute("UPDATE collections SET cats=? WHERE user=?", (' '.join(cats), user))
        else:
            c.execute("INSERT INTO collections (user, cats) VALUES (?, ?)", (user, cat))
        conn.commit()

    def get_user_collection(self, user):
        """Retrieve the user's collection of cats from the database."""
        c.execute("SELECT cats FROM collections WHERE user=?", (user,))
        row = c.fetchone()
        return row[0].split() if row else []


bot = Bot()
bot.run()
