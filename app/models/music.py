from pydantic import BaseModel

class MusicResponse(BaseModel):
    title: str
    description: str
    duration: int
    url: str
    stream_url: str