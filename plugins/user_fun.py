from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("font", prefixes=".") & filters.me)
async def change_font(c: Client, m: Message):
    if len(m.command) < 2: return await m.edit_text("❌ *Tulis teks!*")
    text = m.text.split(None, 1)[1]
    style_text = "".join([chr(ord(char) + 0xFE00) if 'A' <= char <= 'Z' else char for char in text])
    await m.edit_text(f"🎭 **Font Stylist:**\n{style_text}")

# Fitur Fun & Text Style Tambahan:
# .mock | .bold | .italic | .mono | .strike | .underline | .spoiler | .reverse | .slap | .hug | .pat | .dice | .dart | .basketball | .slot | .roll | .flip | .quote | .carbon
