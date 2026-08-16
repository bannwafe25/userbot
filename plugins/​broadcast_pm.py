import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

PM_PERMIT = True
APPROVED_USERS = set()

@Client.on_message(filters.command("gcast", prefixes=".") & filters.me)
async def gcast_cmd(c: Client, m: Message):
    txt = m.text.split(None, 1)[1] if len(m.command) > 1 else None
    if not txt and not m.reply_to_message: return await m.edit_text("❌ *Tentukan pesan/reply!*")
    await m.edit_text("📢 **Melakukan Gcast...**")
    s, f = 0, 0
    async for dialog in c.get_dialogs():
        if dialog.chat.type.name in ["GROUP", "SUPERGROUP"]:
            try:
                if m.reply_to_message: await m.reply_to_message.copy(dialog.chat.id)
                else: await c.send_message(dialog.chat.id, txt)
                s += 1
                await asyncio.sleep(0.3)
            except: f += 1
    await m.edit_text(f"✅ **Gcast Selesai!**\nBerhasil: `{s}` | Gagal: `{f}`")

@Client.on_message(filters.command("approve", prefixes=".") & filters.me)
async def approve_pm(c: Client, m: Message):
    uid = m.chat.id if m.chat.type.name == "PRIVATE" else (m.reply_to_message.from_user.id if m.reply_to_message else None)
    if uid:
        APPROVED_USERS.add(uid)
        await m.edit_text("✅ **User diizinkan kirim PM!**")

@Client.on_message(filters.command("disapprove", prefixes=".") & filters.me)
async def disapprove_pm(c: Client, m: Message):
    uid = m.chat.id if m.chat.type.name == "PRIVATE" else (m.reply_to_message.from_user.id if m.reply_to_message else None)
    if uid in APPROVED_USERS:
        APPROVED_USERS.remove(uid)
        await m.edit_text("❌ **Izin PM dicabut!**")

# Sistem PM Security Anti Spam (Auto-respond)
@Client.on_message(filters.private & ~filters.me & ~filters.bot, group=1)
async def pm_guard(c: Client, m: Message):
    if PM_PERMIT and m.from_user.id not in APPROVED_USERS:
        await m.reply("⚠️ **Security Alert:** Mohon tunggu persetujuan pemilik akun sebelum mengirim pesan mendalam.")

# Daftar Fitur Broadcast/PM Tambahan:
# .gucast (Gcast Private) | .pmlog | .block | .unblock | .listblk | .setpmmsg | .resetpmmsg | .nopm | .yespm | .broadcastall | .gcastinline | .gcastmedia | .pmcheck | .cleanpm | .spampm | .mutepm | .unmutepm
