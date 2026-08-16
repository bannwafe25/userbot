import os, yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("song", prefixes=".") & filters.me)
async def download_song(c: Client, m: Message):
    if len(m.command) < 2: return await m.edit_text("❌ *Judul lagu mana?*")
    query = " ".join(m.command[1:])
    await m.edit_text(f"🔍 *Mencari:* `{query}`...")
    
    ydl_opts = {'format': 'bestaudio', 'outtmpl': '%(title)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        filename = ydl.prepare_filename(info)
        
    await m.edit_text("📥 *Mengirim Musik...*")
    await c.send_audio(m.chat.id, filename)
    os.remove(filename)
    await m.delete()

# Fitur Media Tambahan:
# .video | .ytaudio | .ytvideo | .tiktok | .igdl | .fb | .tw | .spotify | .lyrics | .shazam | .tts | .ss | .qrc | .readqr | .thumb | .gif | .sticker | .toimg | .tosticker

