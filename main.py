import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp

# todo: autoplay, next command, and better queue implementation (create a queue object?)

YDL_OPTS = {
    'format': 'bestaudio',
    'noplaylist': True,
    'extract_audio': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
}

music_queue = []
current = None

# SETUP
load_dotenv()
TOKEN = os.getenv("discord_token")
FFMPEG_PATH = os.getenv("ffmpeg_path")

Intents = discord.Intents().default()
Intents.message_content = True
Bot = commands.Bot(command_prefix='+', intents=Intents)


@Bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
        return False
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        return True


@Bot.command(name='play', help='Searches for and plays the song')
async def play(ctx, *args):
    if not ctx.voice_client:
        if not await join(ctx):
            return
    vc = ctx.voice_client
    if len(args) == 0:
        if current is None:
            await start_audio(ctx)
            return
        else:
            await ctx.send(f"Already playing **{current['title']}**!")

    info = add_to_queue(" ".join(args), front=True)
    if not vc.is_playing():
        await start_audio(ctx)
        await ctx.send(f"Playing **{info['title']}**")
    else:
        await ctx.send(f"Added **{info['title']}** to queue")


@Bot.command(name='queue', help="Adds a song to the queue")
async def queue(ctx, *args):
    if len(args) == 0:
        await show_queue(ctx)
        return
    info = add_to_queue(" ".join(args))
    await ctx.send(f"Added **{info['title']}** to queue")


async def show_queue(ctx):
    string = ', '.join((i['title'] for i in music_queue))
    await ctx.send("Current queue: " + string)


def add_to_queue(query, front=False):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    if front:
        music_queue.insert(0, info)
    else:
        music_queue.append(info)
    return info


async def start_audio(ctx):
    if len(music_queue) == 0:
        await ctx.send("No songs in queue!")
        return
    global current
    current = music_queue.pop(0)
    ctx.voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=current['url'], **ffmpeg_options))


@Bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
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


@Bot.command
async def test(ctx):
    voice_client = ctx.voice_client
    voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source="Fantasia.mp3", **ffmpeg_options))


if __name__ == '__main__':
    Bot.run(TOKEN)
