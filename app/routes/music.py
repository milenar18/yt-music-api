from fastapi import APIRouter, HTTPException
from app.services.youtube_service import get_video_info
from fastapi.responses import StreamingResponse
import requests

from app.services.youtube_service import get_audio_stream
from app.services.youtube_service import search_music

router = APIRouter()

@router.get("/music")
def get_music(url: str):
    try:
        data = get_video_info(url)

        return {
            "title": data["title"],
            "description": data["description"],
            "duration": data["duration"],
            "url": data["webpage_url"],
            "stream_url": data["stream_url"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/play")
def play_music(url: str):
    try:
        data = get_audio_stream(url)
        stream_url = data["stream_url"]

        import requests
        response = requests.get(stream_url, stream=True)

        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type=response.headers.get("Content-Type", "audio/mpeg")
        )

    except Exception as e:
        print("ERRO PLAY:", e)
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/search")
def search(query: str):
    data = search_music(query)
    return data