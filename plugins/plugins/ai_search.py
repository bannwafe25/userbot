import google.generativeai as genai, requests
from pyrogram import Client, filters
from pyrogram.types import Message

genai.configure(api_key="YOUR_GEMINI_API_KEY")

@Client.on_message(filters.command("ai", prefixes=".") & filters.me)
async def ai_query(c: Client, m: Message):
    if len(m.command) < 2: return await m.edit_text("❌ *Tulis pertanyaan!*")
    prompt = m.text.split(None, 1)[1]
    await m.edit_text("🤖 *AI Sedang Berpikir...*")
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    await m.edit_text(f"🤖 **Jawaban AI:**\n\n{response.text}")

@Client.on_message(filters.command("ip", prefixes=".") & filters.me)
async def ip_lookup(c: Client, m: Message):
    if len(m.command) < 2: return await m.edit_text("❌ *Masukkan Alamat IP!*")
    ip = m.command[1]
    res = requests.get(f"https://ipapi.co/{ip}/json/").json()
    await m.edit_text(f"🌐 **IP:** `{res.get('ip')}`\n🏙 **Kota:** `{res.get('city')}`\n🏳 **Negara:** `{res.get('country_name')}`\n📡 **ISP:** `{res.get('org')}`")

# Fitur AI & Search Tambahan:
# .chatgpt | .dalle | .bing | .google | .wiki | .translate | .tr | .urban | .weather | .covid | .chord | .alkitab | .quran | .neko | .waifu | .shorturl | .unshort

