import random
import requests
from pyrogram.enums import *
from pyrogram import *
from pyrogram.types import *
from io import BytesIO

from helpers import Emoji, CMD, animate_proses
from clients import navy

__MODULES__ = "Wallpaper"
__HELP__ = """<blockquote>Command help **Wallpaper**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search Wallpaper**
        `{0}wall2` (query)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

URLS = {
    "teknologi": "https://api.botcahx.eu.org/api/wallpaper/teknologi?apikey=6MWhFzXS",
    "aesthetic": "https://api.botcahx.eu.org/api/wallpaper/aesthetic?apikey=6MWhFzXS",
    "katakata": "https://api.botcahx.eu.org/api/wallpaper/katakata?apikey=6MWhFzXS",
    "heker": "https://api.botcahx.eu.org/api/wallpaper/hacker?apikey=6MWhFzXS",
    "anjing": "https://api.botcahx.eu.org/api/wallpaper/anjing?apikey=6MWhFzXS",
    "hp": "https://api.botcahx.eu.org/api/wallpaper/wallhp?apikey=6MWhFzXS",
    "gamer": "https://api.botcahx.eu.org/api/wallpaper/gaming?apikey=6MWhFzXS",
    "progaming": "https://api.botcahx.eu.org/api/wallpaper/programing?apikey=6MWhFzXS",
    "chuky": "https://api.botcahx.eu.org/api/wallpaper/boneka-chucky?apikey=6MWhFzXS",
    "kucing": "https://api.botcahx.eu.org/api/wallpaper/kucing?apikey=6MWhFzXS",
    }


@CMD.UBOT("wall2")
async def _(client, message, *args):
    em = Emoji(client)
    await em.get()
    query = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if query not in URLS:
        valid_queries = ", ".join(URLS.keys())
        await message.reply(f"<blockquote expandable>{em.gagal} **Query tidak valid. Gunakan salah satu dari: {valid_queries}.**</blockquote>")
        return

    processing_msg = await animate_proses(message, em.proses)
    
    try:
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        response = requests.get(URLS[query])
        response.raise_for_status()
        
        photo = BytesIO(response.content)
        photo.name = 'image.jpg'
        
        await client.send_photo(message.chat.id, photo)
        await processing_msg.delete()
    except requests.exceptions.RequestException as e:
        await processing_msg.edit_text(f"<blockquote>{em.gagal} **Gagal mengambil gambar anime Error: {e}**</blockquote>")
