import discord
import asyncio
from tweepy import OAuthHandler, Stream, StreamListener
from multiprocessing import Queue
from secrets import *


class TwitterListener(StreamListener):
    def on_data(self, data):
        q.put(data)
        return True

    def on_error(self, status):
        print(status)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print(f"Logged in as\n{self.user.name}\n{self.user.id}\n")

        twitter_listener = TwitterListener()

        twitter_auth = OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        twitter_auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

        twitter_stream = Stream(twitter_auth, twitter_listener)
        twitter_stream.filter(follow=[TWITTER_ACCOUNT_TO_FOLLOW])

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!koca"):
            await message.channel.send(
                "Ben Dr. Fahrettin Koca. {0.author.mention}".format(message)
            )

    async def my_background_task(self):
        await self.wait_until_ready()

        channel = self.get_channel(DISCORD_CHANNEL_ID)

        while not self.is_closed():
            while q.not_empty:
                await channel.send(str(q.get()))
                await asyncio.sleep(1)

            await asyncio.sleep(60)


q = Queue()

client = MyClient()
client.run(DISCORD_TOKEN)
