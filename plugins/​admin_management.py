import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

@Client.on_message(filters.command("ban", prefixes=".") & filters.me)
async def ban_user(c: Client, m: Message):
    if not m.reply_to_message: return await m.edit_text("❌ *Reply user!*")
    await c.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.edit_text(f"🚫 **Banned:** {m.reply_to_message.from_user.mention}")

@Client.on_message(filters.command("unban", prefixes=".") & filters.me)
async def unban_user(c: Client, m: Message):
    if not m.reply_to_message: return await m.edit_text("❌ *Reply user!*")
    await c.unban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
    await m.edit_text(f"✅ **Unbanned:** {m.reply_to_message.from_user.mention}")

@Client.on_message(filters.command("kick", prefixes=".") & filters.me)
async def kick_user(c: Client, m: Message):
    if not m.reply_to_message: return await m.edit_text("❌ *Reply user!*")
    uid = m.reply_to_message.from_user.id
    await c.ban_chat_member(m.chat.id, uid)
    await c.unban_chat_member(m.chat.id, uid)
    await m.edit_text(f"👞 **Kicked:** {m.reply_to_message.from_user.mention}")

@Client.on_message(filters.command("mute", prefixes=".") & filters.me)
async def mute_user(c: Client, m: Message):
    if not m.reply_to_message: return await m.edit_text("❌ *Reply user!*")
    await c.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, ChatPermissions())
    await m.edit_text(f"🔇 **Muted:** {m.reply_to_message.from_user.mention}")

@Client.on_message(filters.command("unmute", prefixes=".") & filters.me)
async def unmute_user(c: Client, m: Message):
    if not m.reply_to_message: return await m.edit_text("❌ *Reply user!*")
    await c.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, ChatPermissions(can_send_messages=True))
    await m.edit_text(f"🔊 **Unmuted:** {m.reply_to_message.from_user.mention}")

@Client.on_message(filters.command("pin", prefixes=".") & filters.me)
async def pin_msg(c: Client, m: Message):
    if m.reply_to_message:
        await c.pin_chat_message(m.chat.id, m.reply_to_message.id)
        await m.edit_text("📌 **Pesan disematkan!**")

@Client.on_message(filters.command("unpin", prefixes=".") & filters.me)
async def unpin_msg(c: Client, m: Message):
    await c.unpin_chat_message(m.chat.id)
    await m.edit_text("📌 **Sematkan dilepas!**")

@Client.on_message(filters.command("purge", prefixes=".") & filters.me)
async def purge_msgs(c: Client, m: Message):
    if not m.reply_to_message: return await m.edit_text("❌ *Reply pesan awal!*")
    ids = list(range(m.reply_to_message.id, m.id + 1))
    await c.delete_messages(m.chat.id, ids)

@Client.on_message(filters.command("del", prefixes=".") & filters.me)
async def del_msg(c: Client, m: Message):
    if m.reply_to_message:
        await c.delete_messages(m.chat.id, [m.reply_to_message.id, m.id])

@Client.on_message(filters.command("zombies", prefixes=".") & filters.me)
async def clean_zombies(c: Client, m: Message):
    count = 0
    async for member in c.get_chat_members(m.chat.id):
        if member.user.is_deleted:
            try:
                await c.ban_chat_member(m.chat.id, member.user.id)
                count += 1
            except: pass
    await m.edit_text(f"🧹 **Ditemukan & dibersihkan {count} akun terhapus!**")

# Daftar Fitur Admin Tambahan (Format Ringkas Eksekusi)
# .promote | .demote | .settitle | .setgpic | .delgpic | .setgtitle | .setgdesc | .lock | .unlock | .invite
