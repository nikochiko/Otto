import asyncio
import random
from asyncio import sleep

import discord
import requests

import config


token = config.token


class Matcher:
    def __init__(self):
        self.queue = []
        self.matches = {}

    async def find_match(self, item):
        if len(self.queue) > 0:
            matched_item = self.queue.pop(0)
            self.matches[item] = matched_item
            self.matches[matched_item] = item
            return matched_item
        else:
            self.queue.append(item)
            while item in self.queue:
                await sleep(2)
            return self.matches[item]

    def get_existing_match(self, item):
        return self.matches.get(item)

    def is_in_queue(self, item):
        return item in self.queue

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

        elif message.content.startswith("$otto"):
            await message.channel.send("Hello!")

        elif "otto" in message.content.lower():
            await message.reply("bhow wow")

        elif message.content.startswith("$join"):
            if not await self.get_voice_client(message):
                return await message.reply("You're not connected to a voice channel")

        elif message.content.startswith("$disconnect"):
            client = await self.get_voice_client(message)
            if client:
                return await client.disconnect()
            else:
                return await message.reply("You're not connected to a voice channel")

        elif ("send pics" in message.content.lower()
                or "send nudes" in message.content.lower()):
            url = requests.get("http://shibe.online/api/shibes?count=1").json()[0]
            await message.reply(
                "bow wow",
                embed=discord.Embed(
                    description="bow", title="wow").set_image(url=url))

        elif message.content.startswith("$guess"):
            await message.channel.send("Guess a number between 1 and 10")

            is_valid = lambda m: m.author == message.author and m.content.isdigit()

            answer = random.randint(1, 10)

            tries = 3
            for try_number in range(1, tries+1):
                try:
                    guess = await self.wait_for("message", check=is_valid, timeout=5.0)
                except asyncio.TimeoutError:
                    return await message.channel.send(f"You took too long! It was {answer}")

                guess_number = int(guess.content)
                if guess_number == answer:
                    return await guess.reply("You got it!")
                elif try_number == tries:
                    return await guess.reply(f"Oops. It was {answer}")
                else:
                    remaining = tries - try_number
                    helper = "bigger" if answer > guess_number else "smaller"
                    await guess.reply(f"Nope, {helper}. You have {remaining} more tries")

        elif message.content.startswith("$matchme"):
            if self.matcher.is_in_queue(message.channel):
                return await message.reply("**You're already in the matching queue. Wait till we find someone**")
            elif self.matcher.get_existing_match(message.channel):
                return await message.reply("**You're already connected. Use `$unmatch` to unmatch and try fresh.**")

            await message.reply("**Alright, connecting you rn... 🐶**")
            other_channel = await self.matcher.find_match(message.channel)
            await message.channel.send(f"**Found a match! {other_channel.name}**")

        elif message.content.startswith("$unmatch"):
            other_channel = self.matcher.remove_match(message.channel)
            if other_channel:
                await message.reply("**Unmatched**")
                await other_channel.send("**The other party unmatched.**")
            else:
                await message.reply("Wasn't in an active match")

        elif message.content.startswith("$"):
            clips = {
                "bark": "media/dogbark.ogg",
                "meow": "media/meow.ogg",
            }
            client = await self.get_voice_client(message)
            if client:
                clipname = message.content.strip()[1:]
                clippath = clips.get(clipname)
                if clippath:
                    client.play(discord.FFmpegPCMAudio(clippath))
                    return await message.add_reaction("✅")
            else:
                return await message.reply("You're not connected to a voice channel")

        elif (other_channel := self.matcher.get_existing_match(message.channel)):
            return await other_channel.send(f"**{message.author.name}:** {message.content}")


intents = discord.Intents.default()
intents.message_content = True

client = Otto(intents=intents)
client.run(token)
