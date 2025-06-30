# schemas.py

from pydantic import BaseModel
from datetime import datetime

# --- Veri Okuma Şemaları (Response Modelleri) ---

class Artist(BaseModel):
    ArtistID: int
    ArtistName: str

class Album(BaseModel):
    AlbumID: int
    AlbumTitle: str
    ArtistID: int
    ReleaseYear: int | None = None
    CoverImageUrl: str | None = None

class Song(BaseModel):
    SongID: int
    SongTitle: str
    AlbumTitle: str | None = None
    ArtistName: str | None = None
    DurationSeconds: int
    AudioUrl: str | None = None

class Playlist(BaseModel):
    PlaylistID: int
    PlaylistName: str
    UserID: int
    CreationDate: datetime
    CoverImageUrl: str | None = None

# --- Veri Yazma/Oluşturma Şemaları (Request Body Modelleri) ---

class ArtistCreate(BaseModel):
    ArtistName: str

class AlbumCreate(BaseModel):
    AlbumTitle: str
    ArtistID: int
    ReleaseYear: int

class SongCreate(BaseModel):
    SongTitle: str
    AlbumID: int
    DurationSeconds: int

class PlaylistCreate(BaseModel):
    PlaylistName: str
    UserID: int

class PlaylistUpdate(BaseModel):
    PlaylistName: str