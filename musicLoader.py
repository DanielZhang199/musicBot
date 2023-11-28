import yt_dlp

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


class AudioQueue:
    # Class that handles adding and removing music to queue from links
    def __init__(self):
        self._queue = []
        self.current = None

    def add_by_query(self, query, front=False):
        """
        adds song info to queue; currently works for yt search terms (and links) only
        :param query: (string)
        :param front: (bool) priority; whether method adds to front of queue
        :return: (string) name of song added
        """
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        if front:
            self._queue.insert(0, info)
        else:
            self._queue.append(info)

        return info['title']

    def pop_next(self):
        if len(self._queue) == 0:
            self.current = None
        else:
            self.current = self._queue.pop(0)
        return self.current

    def current_queue(self):
        return tuple(self._queue)

    def now_playing(self):
        return self.current['title']

    def size(self):
        return len(self._queue)


