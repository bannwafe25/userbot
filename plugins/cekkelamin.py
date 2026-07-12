import asyncio
import random

from clients import navy
from helpers import Emoji, CMD

IS_BASIC = True

@CMD.UBOT("cekkontol|cekkntl")
async def cekkhodam(client, message):
    try:
        nama = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not nama:
            await message.edit("ɴᴀᴍᴀɴʏᴀ ᴍᴀɴᴀ ᴀɴᴊᴇɴɢ🤓")
            return

        def pick_random(options):
            return random.choice(options)

        hasil = f"""
<b>𖤐 ᴄᴇᴋ ᴋᴏɴᴛᴏʟ {nama} </b>
<blockquote><b>╭───「 ʜᴀsɪʟ ᴄᴇᴋ ᴋᴏɴᴛᴏʟ 」───</b>
<b>┆• ᴡᴀʀɴᴀ ᴋᴏɴᴛᴏʟ : {pick_random(['irenk', 'pink', 'rainbow', 'itam cok', 'kuning'])}</b>
<b>┆• ᴡᴀʀɴᴀ ᴊᴇᴍʙᴜᴛ : {pick_random(['irenk', 'pink', 'rainbow', 'itam cok', 'kuning'])}</b>
<b>┆• ᴜᴋᴜʀᴀɴ ᴋᴏɴᴛᴏʟ : {pick_random(['16 cm', '10 cm', '15 cm', '6 cm', '1 cm', '3 cm'])}</b>
<b>┆• ᴄɪʀɪ ᴄɪʀɪɴʏᴀ : {pick_random(['bengkok', 'bengkok dikit', 'lurus', 'panjang kecil', 'lebar', 'tumpul'])}</b>
<b>╰──────────────────────</b></blockquote>
  <b>ɴᴇxᴛ ᴄᴇᴋ ᴋᴏɴᴛᴏʟɴʏᴀ sɪᴀᴘᴀ ʟᴀɢɪ.</b>   
      """
        await message.edit(hasil)
    except BaseException:
        pass

@CMD.UBOT("cekmemek|cekmmk")
async def cekkhodam(client, message):
    try:
        nama = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not nama:
            await message.edit("ɴᴀᴍᴀɴʏᴀ ᴍᴀɴᴀ ᴀɴᴊᴇɴɢ🤓")
            return

        def pick_random(options):
            return random.choice(options)

        hasil = f"""
<b>𖤐 ᴄᴇᴋ ᴍᴇᴍᴇᴋ {nama} </b>
<blockquote><b>╭───「 ʜᴀsɪʟ ᴄᴇᴋ ᴍᴇᴍᴇᴋ 」───</b>
<b>┆• ᴡᴀʀɴᴀ ᴍᴇᴍᴇᴋ : {pick_random(['irenk', 'pink', 'rainbow', 'itam cok', 'kuning'])}</b>
<b>┆• ᴡᴀʀɴᴀ ᴊᴇᴍʙᴜᴛ : {pick_random(['irenk', 'pink', 'rainbow', 'itam cok', 'kuning'])}</b>
<b>┆• ᴜᴋᴜʀᴀɴ ʟᴏʙᴀɴɢ : {pick_random(['16 inc', '10 inc', '15 inc', '6 inc', '1 inc', '3 inc'])}</b>
<b>┆• ᴄɪʀɪ ᴄɪʀɪɴʏᴀ : {pick_random(['berjembut', 'dah jebol', 'bau trasi', 'berlendir', 'lebar itam', 'sempit'])}</b>
<b>╰──────────────────────</b></blockquote>
  <b>ɴᴇxᴛ ᴄᴇᴋ ᴍᴇᴍᴇᴋɴʏᴀ sɪᴀᴘᴀ ʟᴀɢɪ.</b>   
      """
        await message.edit(hasil)
    except BaseException:
        pass

@CMD.UBOT("ceksange|ceksagne")
async def cekkhodam(client, message):
    try:
        nama = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not nama:
            await message.edit("ɴᴀᴍᴀɴʏᴀ ᴍᴀɴᴀ ᴀɴᴊᴇɴɢ🤓")
            return

        def pick_random(options):
            return random.choice(options)

        hasil = f"""
<b>𖤐 ᴄᴇᴋ sᴀɴɢᴇ</b>
<blockquote><b>╭───「 ʜᴀsɪʟ ᴄᴇᴋ sᴀɴɢᴇ 」───</b>
<b>┆• ɴᴀᴍᴀ :  {nama} </b>
<b>┆• sᴀɴɢᴇ : {pick_random(['90%', '95%', '75%', '85%', '100%'])}</b>
<b>┆• sᴀɴɢᴇᴀɴ ᴋᴏɴᴛᴏʟ </b>
<b>╰──────────────────────</b></blockquote>
  <b>ɴᴇxᴛ ᴄᴇᴋ sᴀɴɢᴇ sɪᴀᴘᴀ ʟᴀɢɪ.</b>   
      """
        await message.edit(hasil)
    except BaseException:
        pass
__MODULES__ = "Cek kelamin"
__HELP__ = """<blockquote>Command Help **Cek kelamin**</blockquote>

<blockquote expandable>**Get kelamin orang**
    **Cek kelamin orang command**
        `{0}cekkontol` (name)
        `{0}cekmemek` (name)
    **Cek kesangean orang command**
        `{0}ceksange` (name)</blockquote>
    
<b>   {1}</b>
"""
