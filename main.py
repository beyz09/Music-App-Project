# main.py (DÜZELTİLMİŞ)

import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import execute_query, execute_non_query
import schemas

app = FastAPI(
    title="Kişisel Müzik Arşivi",
    description="FastAPI ve Jinja2 ile oluşturulmuş tam fonksiyonel müzik çalar."
)

# --- KLASÖR VE STATİK DOSYA YAPILANDIRMASI ---
os.makedirs("wwwroot/images", exist_ok=True)
os.makedirs("wwwroot/audio", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="wwwroot"), name="media")
templates = Jinja2Templates(directory="templates")

# === YARDIMCI FONKSİYON ===
def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    try:
        folder_name = os.path.basename(destination_folder)
        file_extension = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(destination_folder, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return f"/media/{folder_name}/{unique_filename}"
    finally:
        upload_file.file.close()

# ==========================================================
#                        WEB ARAYÜZÜ ROTALARI (GET)
# ==========================================================
@app.get("/", response_class=HTMLResponse, name="home")
async def get_home_page(request: Request):
    query = """
        SELECT s.SongID, s.SongTitle, s.DurationSeconds, s.AudioUrl, s.CoverArtUrl, 
               al.AlbumTitle, ar.ArtistName
        FROM Songs s
        LEFT JOIN Albums al ON s.AlbumID = al.AlbumID
        LEFT JOIN Artists ar ON al.ArtistID = ar.ArtistID
        ORDER BY s.SongID DESC
    """
    songs = execute_query(query)
    return templates.TemplateResponse("index.html", {"request": request, "songs": songs})

# ... (diğer GET rotaları aynı kalabilir, doğru görünüyorlar)
@app.get("/songs/add", response_class=HTMLResponse, name="add_song_form")
async def get_add_song_form(request: Request):
    albums = execute_query("SELECT al.AlbumID, al.AlbumTitle, ar.ArtistName FROM Artists ar JOIN Albums al ON ar.ArtistID = al.ArtistID ORDER BY ar.ArtistName, al.AlbumTitle")
    return templates.TemplateResponse("manage_song.html", {"request": request, "albums": albums, "song": None, "title": "Yeni Şarkı Ekle"})

@app.get("/songs/edit/{song_id}", response_class=HTMLResponse, name="edit_song_form")
async def get_edit_song_form(request: Request, song_id: int):
    song_data = execute_query("SELECT * FROM Songs WHERE SongID = ?", (song_id,))
    if not song_data:
        raise HTTPException(status_code=404, detail="Şarkı bulunamadı")
    albums = execute_query("SELECT al.AlbumID, al.AlbumTitle, ar.ArtistName FROM Artists ar JOIN Albums al ON ar.ArtistID = al.ArtistID ORDER BY ar.ArtistName, al.AlbumTitle")
    return templates.TemplateResponse("manage_song.html", {"request": request, "albums": albums, "song": song_data[0], "title": "Şarkı Düzenle"})

@app.get("/playlists", response_class=HTMLResponse, name="playlists_list")
async def get_playlists_page(request: Request):
    playlists = execute_query("{CALL sp_GetUserPlaylists (?)}", (1,))
    return templates.TemplateResponse("playlists.html", {"request": request, "playlists": playlists})

@app.get("/playlist/{playlist_id}", response_class=HTMLResponse, name="playlist_detail")
async def get_playlist_detail_page(request: Request, playlist_id: int):
    playlist_info = execute_query("SELECT * FROM Playlists WHERE PlaylistID = ?", (playlist_id,))
    if not playlist_info:
        raise HTTPException(status_code=404, detail="Çalma listesi bulunamadı")
    songs_in_playlist = execute_query("{CALL sp_GetSongsInPlaylist (?)}", (playlist_id,))
    all_songs = execute_query("SELECT SongID, SongTitle FROM Songs ORDER BY SongTitle")
    return templates.TemplateResponse("playlist_detail.html", {
        "request": request, "playlist": playlist_info[0], 
        "songs_in_playlist": songs_in_playlist, "all_songs": all_songs
    })

# ==========================================================
#                        FORM İŞLEME ROTALARI (POST)
# ==========================================================
@app.post("/songs/add", name="add_song")
async def process_add_song(song_title: str = Form(...), album_id: int = Form(...), duration: int = Form(...), audio_file: Optional[UploadFile] = File(None), cover_art_file: Optional[UploadFile] = File(None)):
    audio_url = None
    if audio_file and audio_file.filename:
        audio_url = save_upload_file(audio_file, "wwwroot/audio")
    cover_art_url = None
    if cover_art_file and cover_art_file.filename:
        cover_art_url = save_upload_file(cover_art_file, "wwwroot/images")
    execute_non_query("INSERT INTO Songs (SongTitle, AlbumID, DurationSeconds, AudioUrl, CoverArtUrl) VALUES (?, ?, ?, ?, ?)", (song_title, album_id, duration, audio_url, cover_art_url))
    return RedirectResponse(url=app.url_path_for('home'), status_code=303)

@app.post("/songs/edit/{song_id}", name="edit_song")
async def process_edit_song(song_id: int, song_title: str = Form(...), album_id: int = Form(...), duration: int = Form(...), audio_file: Optional[UploadFile] = File(None), cover_art_file: Optional[UploadFile] = File(None)):
    # ... (Bu fonksiyon doğru görünüyor)
    current_song = execute_query("SELECT AudioUrl, CoverArtUrl FROM Songs WHERE SongID = ?", (song_id,))
    if not current_song:
        raise HTTPException(status_code=404, detail="Güncellenecek şarkı bulunamadı.")
    audio_url = current_song[0].get('AudioUrl')
    if audio_file and audio_file.filename:
        if audio_url:
            old_file_path = "wwwroot" + audio_url.replace("/media", "")
            if os.path.exists(old_file_path): os.remove(old_file_path)
        audio_url = save_upload_file(audio_file, "wwwroot/audio")
    cover_art_url = current_song[0].get('CoverArtUrl')
    if cover_art_file and cover_art_file.filename:
        if cover_art_url:
            old_file_path = "wwwroot" + cover_art_url.replace("/media", "")
            if os.path.exists(old_file_path): os.remove(old_file_path)
        cover_art_url = save_upload_file(cover_art_file, "wwwroot/images")
    execute_non_query("UPDATE Songs SET SongTitle = ?, AlbumID = ?, DurationSeconds = ?, AudioUrl = ?, CoverArtUrl = ? WHERE SongID = ?", (song_title, album_id, duration, audio_url, cover_art_url, song_id))
    return RedirectResponse(url=app.url_path_for('home'), status_code=303)


# === DÜZELTİLEN FONKSİYON ===
@app.post("/songs/delete/{song_id}", name="delete_song")
async def process_delete_song(song_id: int):
    # 1. Dosyaları diskten sil
    song_data = execute_query("SELECT AudioUrl, CoverArtUrl FROM Songs WHERE SongID = ?", (song_id,))
    if song_data:
        if song_data[0].get('AudioUrl'):
            audio_path = "wwwroot" + song_data[0]['AudioUrl'].replace("/media", "")
            if os.path.exists(audio_path): os.remove(audio_path)
        if song_data[0].get('CoverArtUrl'):
            cover_path = "wwwroot" + song_data[0]['CoverArtUrl'].replace("/media", "")
            if os.path.exists(cover_path): os.remove(cover_path)

    # 2. (YENİ VE KRİTİK ADIM) Şarkıyı tüm çalma listelerinden kaldır
    execute_non_query("DELETE FROM PlaylistSongs WHERE SongID = ?", (song_id,))

    # 3. Son olarak şarkının kendisini sil
    execute_non_query("DELETE FROM Songs WHERE SongID = ?", (song_id,))
    
    return RedirectResponse(url=app.url_path_for('home'), status_code=303)

# ... (diğer POST rotaları aynı kalabilir, doğru görünüyorlar)
@app.post("/playlists/add", name="add_playlist")
async def process_add_playlist(playlist_name: str = Form(...)):
    execute_non_query("INSERT INTO Playlists (PlaylistName, UserID) VALUES (?, ?)", (playlist_name, 1))
    return RedirectResponse(url=app.url_path_for('playlists_list'), status_code=303)

@app.post("/playlists/delete/{playlist_id}", name="delete_playlist")
async def process_delete_playlist(playlist_id: int):
    execute_non_query("DELETE FROM Playlists WHERE PlaylistID = ?", (playlist_id,))
    return RedirectResponse(url=app.url_path_for('playlists_list'), status_code=303)

@app.post("/playlist/{playlist_id}/add_song", name="add_song_to_playlist")
async def process_add_song_to_playlist(playlist_id: int, song_id: int = Form(...)):
    execute_non_query("{CALL sp_AddSongToPlaylist (?, ?)}", (playlist_id, song_id))
    return RedirectResponse(url=app.url_path_for('playlist_detail', playlist_id=playlist_id), status_code=303)

@app.post("/playlist/{playlist_id}/remove_song/{song_id}", name="remove_song_from_playlist")
async def process_remove_song_from_playlist(playlist_id: int, song_id: int):
    execute_non_query("DELETE FROM PlaylistSongs WHERE PlaylistID = ? AND SongID = ?", (playlist_id, song_id))
    return RedirectResponse(url=app.url_path_for('playlist_detail', playlist_id=playlist_id), status_code=303)

@app.post("/playlist/{playlist_id}/rename", name="rename_playlist")
async def process_rename_playlist(playlist_id: int, new_playlist_name: str = Form(...)):
    execute_non_query("{CALL sp_UpdatePlaylistName (?, ?)}", (playlist_id, new_playlist_name))
    return RedirectResponse(url=app.url_path_for('playlist_detail', playlist_id=playlist_id), status_code=303)

@app.post("/playlist/{playlist_id}/update_cover", name="update_playlist_cover")
async def process_update_playlist_cover(playlist_id: int, cover_image_file: UploadFile = File(...)):
    playlist_data = execute_query("SELECT CoverImageUrl FROM Playlists WHERE PlaylistID = ?", (playlist_id,))
    if playlist_data and playlist_data[0].get('CoverImageUrl'):
        old_file_path = "wwwroot" + playlist_data[0]['CoverImageUrl'].replace("/media", "")
        if os.path.exists(old_file_path): os.remove(old_file_path)
    image_url = save_upload_file(cover_image_file, "wwwroot/images")
    execute_non_query("{CALL sp_UpdatePlaylistCover (?, ?)}", (playlist_id, image_url))
    return RedirectResponse(url=app.url_path_for('playlist_detail', playlist_id=playlist_id), status_code=303)


# ... (API Endpoints kısmı aynı kalabilir)

# ==========================================================
#                        API ENDPOINT'LERİ (İSTEĞE BAĞLI)
# ==========================================================
@app.get("/api/songs", response_model=List[schemas.Song], tags=["API"])
def get_all_songs_api():
    query = """
        SELECT s.SongID, s.SongTitle, s.DurationSeconds, s.AudioUrl, s.CoverArtUrl, 
               al.AlbumTitle, ar.ArtistName
        FROM Songs s
        LEFT JOIN Albums al ON s.AlbumID = al.AlbumID
        LEFT JOIN Artists ar ON al.ArtistID = ar.ArtistID
        ORDER BY s.SongID DESC
    """
    return execute_query(query)

@app.get("/api/playlists/{playlist_id}/songs", response_model=List[schemas.Song], tags=["API"])
def get_songs_in_playlist_api(playlist_id: int):
    return execute_query("{CALL sp_GetSongsInPlaylist (?)}", (playlist_id,))