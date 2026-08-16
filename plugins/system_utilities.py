import os, time, sys, speedtest
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping(c: Client, m: Message):
    start = time.time()
    msg = await m.edit_text("🏓 `Pinging...`")
    end = time.time()
    await msg.edit_text(f"🚀 **Pong!** `{round((end - start) * 1000)}ms`")

@Client.on_message(filters.command("restart", prefixes=".") & filters.me)
async def restart(c: Client, m: Message):
    await m.edit_text("🔄 **Bot Berhasil Di-restart!**")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("speedtest", prefixes=".") & filters.me)
async def speed_test(c: Client, m: Message):
    await m.edit_text("⚡ **Mengecek Kecepatan VPS...**")
    st = speedtest.Speedtest()
    st.get_best_server()
    dl = st.download() / 1024 / 1024
    ul = st.upload() / 1024 / 1024
    await m.edit_text(f"📊 **Hasil Speedtest:**\n📥 **Download:** `{dl:.2f} Mbps`\n📤 **Upload:** `{ul:.2f} Mbps`")

@Client.on_message(filters.command("id", prefixes=".") & filters.me)
async def get_id(c: Client, m: Message):
    text = f"💬 **Chat ID:** `{m.chat.id}`\n"
    if m.reply_to_message: text += f"👤 **User ID:** `{m.reply_to_message.from_user.id}`"
    else: text += f"👤 **ID Kamu:** `{m.from_user.id}`"
    await m.edit_text(text)

# Fitur System Tambahan:
# .uptime | .sysinfo | .logs | .var | .setvar | .delvar | .getvar | .leave | .leaveall | .join | .stats | .repo | .eval | .exec | .bash | .update

