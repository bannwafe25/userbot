from pyrogram import Client, filters
import requests
from helpers import Emoji, CMD
from clients import navy

__MODULES__ = "Artinama"
__HELP__ = """<blockquote>Command Help **Arti nama**</blockquote>

<blockquote expandable>**Cek artinama orang**
    **Artinama command**
        `{0}artinama` (name)</blockquote>
    
<b>   {1}</b>"""


IS_BASIC = True


@CMD.UBOT("artinama")
async def _(client, message, *args):
    em = Emoji(client)
    await em.get()
    if len(message.command) < 2:
        await message.reply_text("<blockquote>{em.gagal}<b>**Gunakan perintah:** `/artinama nama`\n\nContoh: `/artinama pler`</blockquote></b>")
        return

    nama = " ".join(message.command[1:])
    api_url = f"https://api.siputzx.my.id/api/primbon/artinama?nama={nama}"

    try:
        response = requests.get(api_url).json()

        if response.get("status"):
            nama_res = response["data"]["nama"].title()
            arti_res = response["data"]["arti"]
            catatan_res = response["data"].get("catatan", "")

            reply_text = (
                f"<blockquote><b>**🔍 Arti Nama: {nama_res}**\n\n</blockquote></b>"
                f"<blockquote><b>📖 {arti_res}\n</blockquote></b>"
            )

            if catatan_res:
                reply_text += f"<blockquote><b>\n💡 *{catatan_res}*</blockquote></b>"

            await message.reply_text(reply_text)
        else:
            await message.reply_text(f"<blockquote><b>❌ Maaf, arti nama **{nama}** tidak ditemukan.</blockquote></b>")
    except Exception as e:
        await message.reply_text(f"<blockquote><b>⚠️ Terjadi kesalahan saat mengambil data:\n`{str(e)}`</blockquote></b>")
