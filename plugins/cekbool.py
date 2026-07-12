import asyncio
import random

from clients import navy
from helpers import Emoji, CMD

__MODULES__ = "Cek bool"
__HELP__ = """<blockquote>Command Help **Cek ukuran bool**</blockquote>

<blockquote expandable>**Get bool orang**
    **Cek kelamin orang command**
        `{0}cekbool` (name)</blockquote>
    
<b>   {1}</b>
"""


IS_BASIC = True



@CMD.UBOT("cekbool|bool")
async def cekkhodam(client, message):
    em = Emoji(client)
    await em.get()
    try:
        nama = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not nama:
            await message.edit("<blockquote>**Nama nya mana anj...**</blockquote>")
            return

        def pick_random(options):
            return random.choice(options)

        hasil = f"""
<b>𖤐 ᴄᴇᴋ ʙᴏᴏʟ {nama} </b>
<blockquote><b>╭───「 ʜᴀsɪʟ ᴄᴇᴋ ʙᴏᴏʟ 」───</b>
<b>┆• ᴡᴀʀɴᴀ ʙᴏᴏʟ : {pick_random(['irenk', 'pink', 'rainbow', 'itam cok', 'kuning', 'ijo', 'purple'])}</b>
<b>┆• ᴡᴀʀɴᴀ ʙᴜʟᴜ : {pick_random(['irenk', 'pink', 'rainbow', 'itam cok', 'kuning'])}</b>
<b>┆• ᴜᴋᴜʀᴀɴ ʙᴏᴏʟ : {pick_random(['16 inc', '10 inc', '15 inc', '6 inc', '1 inc', '3 inc', '20 inc'])}</b>
<b>┆• ᴄɪʀɪ ᴄɪʀɪɴʏᴀ : {pick_random(['berbulu', 'dah jebol', 'bau trasi', 'berlendir', 'lebar itam', 'sempit', 'ada sisa tainya'])}</b>
<b>╰──────────────────────</b></blockquote>
  <b>ɴᴇxᴛ ᴄᴇᴋ ʙᴏᴏʟ sɪᴀᴘᴀ ʟᴀɢɪ.</b>   
      """
        await message.edit(hasil)
    except BaseException:
        pass
