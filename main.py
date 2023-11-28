import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from musicLoader import AudioQueue
import asyncio

# todo: fix issue with adding to queue then starting playback

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10',
}

# SETUP
# Env
load_dotenv()
TOKEN = os.getenv("discord_token")
FFMPEG_PATH = os.getenv("ffmpeg_path")

# Discord.py
Intents = discord.Intents().default()
Intents.message_content = True
Bot = commands.Bot(command_prefix='+', intents=Intents)

# Music queue
Queue = AudioQueue()


@Bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
        return False
    else:
        await ctx.message.author.voice.channel.connect()
        return True


@Bot.command(name='play', help='Adds the song to front of queue, starts playback')
async def play(ctx, *args):
    if not ctx.voice_client:
        if not await join(ctx):
            return

    if len(args) == 0:
        if ctx.voice_client.is_playing():
            await ctx.send("Already playing a song!")
        else:
            await start_audio(ctx)
    else:
        name = Queue.add_by_query(" ".join(args), front=True)
        if not ctx.voice_client.is_playing():
            await start_audio(ctx)
        else:
            await ctx.send(f"Added **{name}** to front of queue")


@Bot.command(name='add', help='Searches for and adds the song to queue')
async def add(ctx, *args):
    name = Queue.add_by_query(" ".join(args))
    await ctx.send(f"Added **{name}** to queue")


@Bot.command(name='queue', help="Displays the queue")
async def queue(ctx):
    string = ', '.join((i['title'] for i in Queue.current_queue()))
    await ctx.send("Current queue: " + string)


@Bot.command(name='skip', help="Skips current song")
async def skip(ctx):
    ctx.voice_client.stop()
    await start_audio(ctx)


async def start_audio(ctx):
    if Queue.size() == 0:
        await ctx.send("No songs in queue!")
    else:
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=Queue.pop_next()['url'],
                                                     **ffmpeg_options), after=play_next(ctx))
        await ctx.send(f"Now playing: **{Queue.now_playing()}**")


def play_next(ctx):  # to continue playing while queue still not empty
    if Queue.size() > 0:
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=Queue.pop_next()['url'],
                                                     **ffmpeg_options), after=lambda e: play_next(ctx))
        asyncio.run_coroutine_threadsafe(ctx.send("No more songs in queue."), Bot.loop)


@Bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Not connected to any voice channel.")


@Bot.command(name='stop', help='Stops playback and leaves the voice channel')
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await voice_client.disconnect()
    else:
        await leave(ctx)


if __name__ == '__main__':
    Bot.run(TOKEN)
