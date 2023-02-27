import asyncio
import random
import re
import yaml
from asyncio import sleep

import discord
import requests

from . import db
from . import spotify


with open("clips.yml") as f:
    clips = yaml.safe_load(f)


class Matcher:
    def __init__(self):
        self.queue = []
        self.matches = {}
        self.sleep_interval = 2  # seconds

    async def find_match(self, item):
        if len(self.queue) > 0:
            matched_item = self.queue.pop(0)
            self.matches[item] = matched_item
            self.matches[matched_item] = item
            return matched_item
        else:
            self.queue.append(item)
            while item in self.queue:
                await sleep(self.sleep_interval)
            return self.matches[item]

    def get_existing_match(self, item):
        return self.matches.get(item)

    def is_in_queue(self, item):
        return item in self.queue

    def unqueue(self, item):
        self.queue.remove(item)

    def remove_match(self, item):
        if item in self.matches:
            matched_item = self.matches.pop(item)
            self.matches.pop(matched_item)
            return matched_item
        else:
            return None


class Otto(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matcher = Matcher()
        self.chess_matcher = Matcher()

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def get_voice_client(self, message):
        channel = message.author.voice and message.author.voice.channel
        if channel:
            for voice_client in self.voice_clients:
                if voice_client.channel == channel:
                    return voice_client
                elif voice_client.channel.guild == channel.guild:
                    await voice_client.move_to(channel)
                    return voice_client
            return await channel.connect()

    async def on_message(self, message):
        if message.author == self.user:
            return

        match message.content.strip().split():
            case ["$otto", *_]:
                return await message.channel.send("Hello!")
            case _ if "otto" in message.content.lower():
                return await message.reply("bow wow")
            case ["$join", *_]:
                if not await self.get_voice_client(message):
                    return await message.reply("You're not connected to a voice channel")
            case ["$disconnect", *_]:
                client = await self.get_voice_client(message)
                if client:
                    return await client.disconnect()
                else:
                    return await message.reply("You're not connected to a voice channel")
            case [("$pics" | "$nudes"), *_]:
                url = requests.get("http://shibe.online/api/shibes?count=1").json()[0]
                await message.reply(
                    "bow wow",
                    embed=discord.Embed(
                        description="bow", title="wow").set_image(url=url))
            case ["$matchme", *_]:
                if self.matcher.is_in_queue(message.channel):
                    return await message.reply("**You're already in the matching queue. Wait till we find someone**")
                elif self.matcher.get_existing_match(message.channel):
                    return await message.reply("**You're already connected. Use `$unmatch` to unmatch and try fresh.**")

                await message.reply("**Alright, connecting you rn... 🐶**")
                other_channel = await self.matcher.find_match(message.channel)
                await message.channel.send("**Found a match!**")
            case ["$unmatch", *_]:
                other_channel = self.matcher.remove_match(message.channel)
                if other_channel:
                    await message.reply("**Unmatched**")
                    await other_channel.send("**The other party unmatched.**")
                elif self.matcher.is_in_queue(message.channel):
                    self.matcher.unqueue(message.channel)
                    await message.reply("**Removed from matching queue**")
                else:
                    await message.reply("**Not in a match.**")
            case ["$chess", "random", *args]:
                await message.reply("**Waiting for a match...**")
                other_message = await self.chess_matcher.find_match(message)
                params = parse_chess_params(args)
                url = get_chess_challenge_url(**params)
                await message.reply(f"**Match found.** You're playing vs {other_message.author.name}\n{url}")
                await sleep(self.chess_matcher.sleep_interval)
                self.chess_matcher.remove_match(message)
            case ["$chess", *args] | ["$chess", "lichess", *args]:
                params = parse_chess_params(args)
                url = get_chess_challenge_url(**params)
                await message.reply(url)
            case ["$spotify", "connect"]:
                url = spotify.get_authorize_url(
                    state=str(message.author.id),
                    scope="user-read-playback-state")
                return await message.reply(
                    "",
                    embed=discord.Embed(
                        description=f"Connect by going to [this url]({url}).")
                )
            case ["$spotify", "status"]:
                token = db.get_value("spotify_token", message.author.id)
                if token is None:
                    return await message.reply("Your Spotify isn't connected with me.")
                else:
                    play_state = spotify.get_play_state(token=token)
                    if play_state["state"] == "active":
                        embed = discord.Embed(
                            title=md_link(
                                play_state["track_name"],
                                play_state["track_url"],
                            ),
                            description="From %s.\n%s" % (
                                md_link(play_state["album_name"], play_state["album_url"]),
                                md_link("Preview", play_state["preview_url"]),
                            ),
                        ).set_image(url=play_state["image_url"])
                        return await message.reply("", embed=embed)
                    else:
                        return await message.reply("you ain't playin' nothin")
            case _ if message.content.startswith("$"):
                client = await self.get_voice_client(message)
                if client:
                    clipname = message.content.strip()[1:]
                    clippath = clips.get(clipname)
                    if clippath:
                        client.play(discord.FFmpegPCMAudio(clippath))
                        return await message.add_reaction("✅")
                else:
                    return await message.reply("You're not connected to a voice channel")
            case _ if (other_channel := self.matcher.get_existing_match(message.channel)):
                return await other_channel.send(f"**{message.author.name}:** {message.content}")


def parse_chess_params(params):
    result = {}

    time_control_regex = re.compile(r"([0-9]+)\+([0-9]+)")
    for param in params:
        if (m := time_control_regex.match(param)):
            minutes = int(m.group(1))
            increment = int(m.group(2))
            result.update(clock_limit=minutes*60, clock_increment=increment)

    return result

def get_chess_challenge_url(clock_limit=300, clock_increment=3):
    lichess_url = "https://lichess.org/api/challenge/open"
    response = requests.post(lichess_url, data={"clock.limit": clock_limit, "clock.increment": clock_increment}).json()
    return response["challenge"]["url"]


def md_link(text, href):
    return f"[{text}]({href})"


intents = discord.Intents.default()
intents.message_content = True

client = Otto(intents=intents)
