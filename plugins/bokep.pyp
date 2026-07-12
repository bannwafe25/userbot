import asyncio
import random
from random import choice
from pyrogram.enums import MessagesFilter

from pyrogram import enums, types
from config import OWNER_ID

from helpers import CMD, Emoji

__MODULES__ = "Bokep"
__HELP__ = """<blockquote>Command Help **Bokep**</blockquote>
    
<blockquote><u>**Get videos**</u>
    <u>**Get random bokep video**</u>
        `{0}bokep`</blockquote>
    
<b>   {1}</b>
"""

IS_PRO = True

@CMD.UBOT("bokep")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    y = await message.reply_text(
        f"<blockquote>{em.proses} **mencari video bokep**...</blockquote>", 
        quote=True
    )
    try:
        await client.join_chat("https://t.me/+b0IsegAgAj9kNjY1")
    except:
        pass
    try:
        bokepnya = []
        async for bokep in client.search_messages(
            -1002930105331, filter=MessagesFilter.VIDEO
        ):
            bokepnya.append(bokep)

        if not bokepnya:
            return await y.edit("❌ Tidak ada video ditemukan.")

        # pilih 3 random, kalau kurang ya sesuai jumlah
        pilih = random.sample(bokepnya, min(3, len(bokepnya)))

        for video in pilih:
            await video.copy(message.chat.id, reply_to_message_id=message.id)

        await y.delete()
        await message.reply_text(
            f"<blockquote>{em.sukses} **udah sana ngocokk..**</blockquote>", 
            quote=True
        )
    except Exception as error:
        await y.edit(str(error))

    if client.me.id != OWNER_ID:
        await client.leave_chat(-1002930105331)
