import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

IS_AFK = False
AFK_REASON = ""

@Client.on_message(filters.command("afk", prefixes=".") & filters.me)
async def set_afk(c: Client, m: Message):
    global IS_AFK, AFK_REASON
    IS_AFK = True
    AFK_REASON = " ".join(m.command[1:]) or "Sedang Istirahat."
    await m.edit_text(f"💤 **Mode AFK Aktif!**\n📝 **Alasan:** `{AFK_REASON}`")

@Client.on_message(filters.me, group=-1)
async def unset_afk(c: Client, m: Message):
    global IS_AFK
    if IS_AFK and not m.text.startswith(".afk"):
        IS_AFK = False
        msg = await m.reply("👋 **Saya Kembali Online!**")
        await asyncio.sleep(3)
        await msg.delete()

# Fitur AFK & Profil Tambahan:
# .setname | .setbio | .setpfp | .delpfp | .autobio | .autoname | .clockname | .alive | .help | .setting | .prefix | .clone | .revert | .saved | .reminders | .calc | .pingall

