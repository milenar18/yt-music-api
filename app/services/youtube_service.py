import yt_dlp

def get_video_info(url: str):
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "webpage_url": info.get("webpage_url"),
            "stream_url": info.get("url")
        }

def get_audio_stream(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "stream_url": info.get("url")
        }

def search_music(query: str):
    import yt_dlp

    ydl_opts = {
        'quiet': True,
        'extract_flat': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch10:{query}", download=False)

        musics = []

        entries = results.get('entries')

        if not entries:
            return []

        for entry in entries:
            if not entry:
                continue

            musics.append({
                "title": entry.get("title", "Sem título"),
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                "duration": entry.get("duration", 0)
            })

    return musics