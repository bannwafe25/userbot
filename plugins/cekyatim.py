from pyrogram import Client, filters
import random
from clients import navy
from helpers import Emoji, CMD

__MODULES__ = "Cekyatim"
__HELP__ = """<blockquote>Command Help **Cek Yatim**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Cek kemungkinan menjadi yatim**
        `{0}cyatim` (reply/username)</blockquote>
<b>   {1}</b>
"""

IS_BASIC = True


def emoji(alias):
    emojis = {
        "DETEK": "<emoji id=6100651407860306283>🃏</emoji>",    
        "SUBJEK": "<emoji id=5366186501023481690>😱</emoji>",
        "PERSEN": "<emoji id=5327845276432485469>📊</emoji>",  
        "YATIM": "<emoji id=5434095036394387314>👶</emoji>",   
    }
    return emojis.get(alias, "⎆")


dtk = emoji("DETEK")
subj = emoji("SUBJEK")
pers = emoji("PERSEN")
yatim = emoji("YATIM")


@CMD.UBOT("cyatim")
async def _(client, message, *args):
    em = Emoji(client)
    await em.get()
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user = await client.get_users(message.command[1])
    else:
        user = message.from_user

    if user:
        username = f"@{user.username}" if user.username else user.first_name
        persen_yatim = random.randint(0, 100)

        response = f"""
<blockquote expandable>**__{dtk} Deteksi Yatim {dtk}__**

{subj} **Subjek**: {username}
{pers} **Kemungkinan jadi yatim**: [{persen_yatim}%] {"█" * (persen_yatim // 10)}

{yatim} Semoga selalu diberikan umur panjang & kesehatan 🙏</blockquote>
"""
        await message.reply_text(response)
    else:
        await message.reply_text(f"<blockquote>{em.gagal} **Gagal mendeteksi pengguna...**</blockquote>")
