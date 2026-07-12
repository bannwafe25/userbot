import random
import requests
from pyrogram.enums import *
from pyrogram import *
from pyrogram.types import *
from io import BytesIO

from helpers import Emoji, CMD
from clients import navy

__MODULES__ = "Anime2"
__HELP__ = """<blockquote>Command Help **Anime2**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search your favorite Anime**
        `{0}anime2` (query)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


URLS = {
    "keneki": "https://api.botcahx.eu.org/api/anime/keneki?apikey=Priaindia",
    "megumin": "https://api.botcahx.eu.org/api/anime/megumin?apikey=Priaindia",
    "yotsuba": "https://api.botcahx.eu.org/api/anime/yotsuba?apikey=Priaindia",
    "shinomiya": "https://api.botcahx.eu.org/api/anime/shinomiya?apikey=Priaindia",
    "yumeko": "https://api.botcahx.eu.org/api/anime/yumeko?apikey=Priaindia",
    "tsunade": "https://api.botcahx.eu.org/api/anime/tsunade?apikey=Priaindia",
    "kagura": "https://api.botcahx.eu.org/api/anime/kagura?apikey=Priaindia",
    "madara": "https://api.botcahx.eu.org/api/anime/madara?apikey=Priaindia",
    "itachi": "https://api.botcahx.eu.org/api/anime/itachi?apikey=Priaindia",
    "akira": "https://api.botcahx.eu.org/api/anime/akira?apikey=Priaindia",
    "toukachan": "https://api.botcahx.eu.org/api/anime/toukachan?apikey=Priaindia",
    "cicho": "https://api.botcahx.eu.org/api/anime/chiho?apikey=Priaindia",

}

@CMD.UBOT("anime2")
async def _(client, message, *args):
    # Extract query from message
    query = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if query not in URLS:
        valid_queries = ", ".join(URLS.keys())
        await message.reply(f"<blockquote>Query tidak valid. Gunakan salah satu dari: {valid_queries}.</blockquote>")
        return

    processing_msg = await message.reply("<blockquote>Processing....</blockquote>")
    
    try:
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        response = requests.get(URLS[query])
        response.raise_for_status()
        
        photo = BytesIO(response.content)
        photo.name = 'image.jpg'
        
        await client.send_photo(message.chat.id, photo)
        await processing_msg.delete()
    except requests.exceptions.RequestException as e:
        await processing_msg.edit_text(f"<blockquote>Gagal mengambil gambar anime Error: {e}</blockquote>")
