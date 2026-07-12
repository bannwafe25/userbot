import os
import requests

API_KEY = "6MWhFzXS"

from helpers import Emoji, CMD
from clients import navy

__MODULES__ = "TextPro2"
__HELP__ = """<blockquote>Command Help **Text Pro 2**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Make Text Pro 2**
        `{0}neon`
        `{0}neongalaxy`
        `{0}neongreen`
        `{0}brokenglass`
        `{0}artpapper`</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

def fetch_image(api_url, text):
    """
    Fungsi untuk mengambil gambar dari API
    """
    params = {"text": text, "apikey": API_KEY}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()

        if response.headers.get("Content-Type", "").startswith("image/"):
            return response.content
        else:
            print("Response bukan gambar:", response.text)  # Debugging
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")  # Debugging jika ada kesalahan
        return None

async def process_image_command(client, message, api_url, command_name, *args):
    """
    Fungsi umum untuk menangani perintah pembuatan gambar
    """
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply_text(f"<blockquote><b><i>Gunakan perintah /{command_name} <teks> untuk membuat gambar.</i></b></blockquote>")
        return

    request_text = args[1]
    await message.reply_text("<blockquote><b><i>Sedang memproses, mohon tunggu...</i></b></blockquote>")

    image_content = fetch_image(api_url, request_text)
    if image_content:
        temp_file = f"{command_name}.jpg"
        with open(temp_file, "wb") as f:
            f.write(image_content)
        await message.reply_photo(photo=temp_file)
        os.remove(temp_file)
    else:
        await message.reply_text("<blockquote>Gagal membuat gambar. Coba lagi nanti.</blockquote>")

# Handler untuk setiap perintah
@CMD.UBOT("neon")
async def eraser_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/neon-light"
    await process_image_command(client, message, api_url, "neon-light")

@CMD.UBOT("neongalaxy")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/neon-galaxy"
    await process_image_command(client, message, api_url, "neon-galaxy")

@CMD.UBOT("neongreen")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/neon-green"
    await process_image_command(client, message, api_url, "neon-green")

@CMD.UBOT("brokenglass")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/broken-glass"
    await process_image_command(client, message, api_url, "broken-glass")

@CMD.UBOT("artpapper")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/art-papper"
    await process_image_command(client, message, api_url, "art-papper")
