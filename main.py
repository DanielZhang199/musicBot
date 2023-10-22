import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp

YDL_OPTS = {
    'format': 'bestaudio',
    'noplaylist': 'True',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

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
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()


@Bot.command(name='play', help='Searches for and plays the song')
async def play(ctx, query):
    voice_client = ctx.voice_client
    if not voice_client:
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
            return False
        else:
            voice_client = await ctx.message.author.voice.channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=url2))


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


if __name__ == '__main__':
    Bot.run(TOKEN)
