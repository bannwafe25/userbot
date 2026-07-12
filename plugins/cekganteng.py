import asyncio
import random

from clients import navy
from helpers import CMD, Emoji


__MODULES__ = "Cek ganteng"
__HELP__ = """<blockquote>Command Help **Cek ganteng**</blockquote>

<blockquote expandable>**Cek kegantengan orang**
    **Cek kegantengan orang command**
        `{0}cekganteng` (name)</blockquote>
    
<b>   {1}</b>
"""

IS_BASIC = True

@CMD.UBOT("cekganteng")
async def cekkhodam(client, message):
    try:
        nama = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not nama:
            await message.edit("ɴᴀᴍᴀɴʏᴀ ᴍᴀɴᴀ")
            return

        def pick_random(options):
            return random.choice(options)

        hasil = f"""
 <b>𖤐 ʜᴀsɪʟ ᴄᴇᴋ ɢᴀɴᴛᴇɴɢ:</b>
╭───────────────────────
├ •ɴᴀᴍᴀ : {nama}
├ •ɢᴀɴᴛᴇɴɢ : {pick_random(['ᴋᴀʏᴀ ᴋᴛʟ', 'ᴅɪᴋɪᴛ', 'ʙᴀɴʏᴀᴋ', 'sᴇᴛᴇɴɢᴀʜ', 'sᴇᴘᴇʀᴀᴘᴀᴛ', 'sᴇ ᴛᴇᴛᴇ'])}
├ •ɴɢᴇʀɪ ʙᴇᴛ ᴊɪʀ
╰────────────────────────
  **ɴᴇxᴛ ᴄᴇᴋ ɢᴀɴᴛᴇɴɢ sɪᴀᴘᴀ ʟᴀɢɪ.**       
      """
        await message.edit(hasil)
    except BaseException:
        pass
