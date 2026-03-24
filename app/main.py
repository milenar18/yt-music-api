from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import yt_dlp
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YouTube Music Info API")

# Modelo de resposta
class YouTubeMusicInfo(BaseModel):
    title: str
    artist: str
    duration: int
    thumbnail: Optional[str] = None
    video_id: str
    url: str

async def extract_video_id(url: str) -> str:
    """Extrai o ID do vídeo de uma URL do YouTube"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([\w-]+)',
        r'(?:youtu\.be\/)([\w-]+)',
        r'(?:youtube\.com\/embed\/)([\w-]+)',
        r'(?:youtube\.com\/shorts\/)([\w-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("URL do YouTube inválida")

async def get_youtube_info(url: str) -> dict:
    """Busca informações do vídeo usando yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'force_generic_extractor': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', ''),
                'artist': info.get('uploader', 'Artista Desconhecido'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'video_id': info.get('id', ''),
                'url': url
            }
    except Exception as e:
        raise Exception(f"Erro ao buscar informações: {str(e)}")

@app.get("/", tags=["Status"])
async def root():
    """Verifica se a API está funcionando"""
    return {"message": "YouTube Music Info API", "status": "online"}

@app.get("/music-info", response_model=YouTubeMusicInfo, tags=["YouTube"])
def get_music_info(url: str = Query(..., description="URL do vídeo do YouTube")):
    """
    Obtém informações de uma música/vídeo do YouTube
    
    - **url**: URL completa do vídeo (ex: https://www.youtube.com/watch?v=dQw4w9WgXcQ)
    
    Retorna: título, artista, duração, thumbnail e ID do vídeo
    """
    # Valida se a URL é do YouTube
    if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
        raise HTTPException(status_code=400, detail="URL inválida. Forneça uma URL do YouTube")
    
    try:
        # Extrai e valida o ID
        video_id = extract_video_id(url)
        
        # Busca as informações
        info = get_youtube_info(url)
        
        return YouTubeMusicInfo(**info)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")

@app.get("/search", tags=["YouTube"])
async def search_music(query: str = Query(..., description="Nome da música ou artista")):
    """
    Pesquisa músicas no YouTube por palavra-chave
    
    - **query**: termo de busca (ex: "Bohemian Rhapsody Queen")
    
    Retorna: lista com até 5 resultados
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'playlistend': 5,  # Limita a 5 resultados
    }
    
    search_query = f"ytsearch5:{query}"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            results = []
            
            for entry in info.get('entries', []):
                results.append({
                    'title': entry.get('title', ''),
                    'artist': entry.get('uploader', 'Desconhecido'),
                    'duration': entry.get('duration', 0),
                    'video_id': entry.get('id', ''),
                    'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                })
            
            return {"results": results, "count": len(results)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # libera tudo (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import music
app.include_router(music.router) 