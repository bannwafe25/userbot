import os
import requests

API_KEY = "6MWhFzXS"

from helpers import Emoji, CMD
from clients import navy

__MODULES__ = "TextPro1"
__HELP__ = """<blockquote>Command Help **Text Pro 1**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Make Text Pro 1**
        `{0}giraffe`
        `{0}magma`
        `{0}halloween`
        `{0}valentine`
        `{0}valentine2`</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

def fetch_image(api_url, text):
    params = {"text": text, "apikey": API_KEY}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()

        # Jika langsung gambar
        if response.headers.get("Content-Type", "").startswith("image/"):
            return response.content

        # Jika JSON dengan result
        data = response.json()
        if "result" in data:
            img_url = data["result"]
            img_res = requests.get(img_url)
            img_res.raise_for_status()
            return img_res.content

        print("Response tidak dikenali:", response.text)
        return None
    except Exception as e:
        print(f"Error fetching image: {e}")
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
        await message.reply_text("<blockquote>**Gagal membuat gambar. Coba lagi nanti.**</blockquote>")

# Handler untuk setiap perintah
@CMD.UBOT("giraffe")
async def eraser_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/giraffe"
    await process_image_command(client, message, api_url, "giraffe")

@CMD.UBOT("magma")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/magma"
    await process_image_command(client, message, api_url, "magma")
    
@CMD.UBOT("halloween")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/halloween"
    await process_image_command(client, message, api_url, "halloween")

@CMD.UBOT("valentine")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/valentine"
    await process_image_command(client, message, api_url, "valentine")

@CMD.UBOT("valentine2")
async def papercut_command(client, message, *args):
    api_url = "https://api.botcahx.eu.org/api/textpro/valentine2"
    await process_image_command(client, message, api_url, "valentine2")
