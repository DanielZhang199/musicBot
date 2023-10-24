# Music Bot
A basic Python script for a Discord bot that plays music from Youtube (and thats about it). In future may also work on Spotify/YT Music songs and playlists.

### Commands
- `+join`
- `+leave`
- `+play \<search term|link\>`
- `+stop`
- `+queue`

## Project goals
1. Bot is able to join and leave channels that users are in.
2. Bot can start playing music given a link or query term.
3. `+play` command can start playback, or add to queue depending on scenario.
   1. That means there has to be a queue of next songs.
   2. Users should be able to view queue and remove songs from queue.
4. Bot can display current song playing, and other relevant information.
5. Bot automatically leaves voice channel after being idle for a while.
6. Bot can skip to next song in queue.

> Don't expect anything super polished, but hopefully this project will be functional enough for personal use.