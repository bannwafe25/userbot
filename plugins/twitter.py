import os
import random
import logging
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.types import Message

# --- IMPORT LOCAL ---
from clients import navy
from helpers import CMD
from database import dB

# --- KONFIGURASI MODUL ---
__MODULE__ = "ᴛᴡᴇＥᴛ"
__HELP__ = """<blockquote>Command Help **ᴛᴡᴇᴇᴛ**</blockquote>
<blockquote><b>Bantuan untuk Tweet Image</b>

<b>• Perintah:</b> <code>{0}tweet</code> [teks / reply]
  Membuat gambar tweet mobile 1080px murni, presisi, dan identik dengan contoh screenshot HP.
</blockquote>
"""

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TweetMaker")

# ===== CONFIG VISUAL TWITTER MOBILE 1080P PRESETS =====
BG_COLOR = "#000000"         # Hitam pekat Twitter
WHITE = "#F7F9F9"            # Putih bersih teks utama Twitter
GRAY = "#71767B"             # Abu-abu teks sekunder Twitter
LINE_COLOR = "#2F3336"       # Garis tipis pembatas Twitter asli
VERIFIED_COLOR = "#1DA1F2"   # Biru resmi centang Twitter

# Mengunci ukuran murni sesuai spesifikasi screenshot HP Full HD
CANVAS_WIDTH = 1080          
PADDING_X = 45               # Jarak tepi horizontal presisi

# --- UTILS ---
def circle_avatar(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    img.putalpha(mask)
    return img

def wrap_text_by_pixels(text, font, max_width, draw):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if draw.textlength(test_line, font=font) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines

# --- COMMAND HANDLER ---
@CMD.UBOT("tweet")
async def tweet_cmd_handler(client, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
        user = message.reply_to_message.from_user
    else:
        text = client.get_arg(message)
        user = message.from_user

    if not text:
        return await message.reply("❌ <b>Berikan teks atau reply ke pesan!</b>")

    inf_msg = await message.reply("🔍 <i>Generating Mobile 1080p Tweet...</i>")
    
    try:
        # 1. Download Avatar (Ukuran disesuaikan untuk skala 1080p: 100x100 px)
        if user and user.photo:
            try:
                ava_path = await client.download_media(user.photo.big_file_id)
                avatar = Image.open(ava_path).convert("RGBA").resize((100, 100))
                os.remove(ava_path)
            except Exception:
                avatar = Image.new("RGBA", (100, 100), "#444444")
        else:
            avatar = Image.new("RGBA", (100, 100), "#444444")
            
        avatar = circle_avatar(avatar)

        # 2. Setup Font Sesuai Skala Dimensi 1080p HP
        FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not os.path.exists(FONT_PATH):
            FONT_PATH = "arial.ttf"

        try:
            bold_name_f = ImageFont.truetype(FONT_PATH, 36)    # Nama tebal (36px)
            username_f = ImageFont.truetype(FONT_PATH, 32)      # @username (32px)
            tweet_text_f = ImageFont.truetype(FONT_PATH, 46)    # Isi Tweet utama (46px)
            small_text_f = ImageFont.truetype(FONT_PATH, 28)    # Waktu & Label teks (28px)
            bold_stats_f = ImageFont.truetype(FONT_PATH, 28)    # Angka statistik tebal (28px)
        except:
            bold_name_f = username_f = tweet_text_f = small_text_f = bold_stats_f = ImageFont.load_default()

        dummy_img = Image.new("RGB", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        max_text_width = CANVAS_WIDTH - (PADDING_X * 2)
        lines = wrap_text_by_pixels(text, tweet_text_f, max_text_width, dummy_draw)

        # 3. Hitung Tinggi Dinamis Kompak Layar HP
        line_height = 68   # Jarak vertikal antar baris kalimat (68px)
        header_height = 190
        footer_height = 180 
        dynamic_height = header_height + (len(lines) * line_height) + footer_height
        
        base = Image.new("RGB", (CANVAS_WIDTH, dynamic_height), BG_COLOR)
        base_draw = ImageDraw.Draw(base)

        # 4. Pasang Avatar & Nama (Margin Atas: 45px)
        base.paste(avatar, (PADDING_X, 45), avatar)
        full_name = (user.first_name if user else "User") or "Telegram User"
        user_name = (user.username if user else "anonymous") or "anonymous"

        # Teks Nama Utama diletakkan lurus di koordinat X=175
        base_draw.text((175, 48), full_name, font=bold_name_f, fill=WHITE)
        name_w = base_draw.textlength(full_name, font=bold_name_f)
        
        # Menggambar lencana verifikasi biru tepat di sebelah akhir huruf nama akun
        base_draw.text((175 + name_w + 10, 48), "✔", font=bold_name_f, fill=VERIFIED_COLOR)

        # Teks Username
        base_draw.text((175, 98), f"@{user_name}", font=username_f, fill=GRAY)

        # 5. Render Isi Kalimat Tweet Utama
        current_y = header_height
        for line in lines:
            base_draw.text((PADDING_X, current_y), line, font=tweet_text_f, fill=WHITE)
            current_y += line_height

        # 6. Format Waktu (Kiri) & Jumlah Views (Kanan)
        current_y += 50
        time_str = datetime.now().strftime("%I:%M %p · %d %b %Y").lower()
        
        views_val = f"{random.randint(100, 999)}.{random.randint(100, 999)}"
        views_text = f"{views_val} Views"
        
        base_draw.text((PADDING_X, current_y), time_str, font=small_text_f, fill=GRAY)
        
        v_num_w = base_draw.textlength(views_val, font=bold_stats_f)
        v_lbl_w = base_draw.textlength(" Views", font=small_text_f)
        total_v_w = v_num_w + v_lbl_w
        
        base_draw.text((CANVAS_WIDTH - PADDING_X - total_v_w, current_y), views_val, font=bold_stats_f, fill=WHITE)
        base_draw.text((CANVAS_WIDTH - PADDING_X - total_v_w + v_num_w, current_y), " Views", font=small_text_f, fill=GRAY)

        # ===== SATU-SATUNYA GARIS PEMBATAS TIPIS RESMI (Width=1) =====
        current_y += 50
        base_draw.line([(PADDING_X, current_y), (CANVAS_WIDTH - PADDING_X, current_y)], fill=LINE_COLOR, width=1)

        # 7. Render Baris Statistik Horizontal (Retweets, Quotes, Likes, Bookmarks)
        current_y += 24
        
        rt_c = f"{random.randint(1000, 4999):,}".replace(",", ".")
        qt_c = f"{random.randint(100, 899):,}".replace(",", ".")
        lk_c = f"{random.randint(1000, 4999):,}".replace(",", ".")
        bm_c = f"{random.randint(50, 490):,}".replace(",", ".")
        
        stats_data = [
            (rt_c, "Retweets"),
            (qt_c, "Quotes"),
            (lk_c, "Likes"),
            (bm_c, "Bookmarks")
        ]
        
        start_x = PADDING_X
        for num, label in stats_data:
            base_draw.text((start_x, current_y), num, font=bold_stats_f, fill=WHITE)
            num_w = base_draw.textlength(num, font=bold_stats_f)
            
            base_draw.text((start_x + num_w + 6, current_y), label, font=small_text_f, fill=GRAY)
            lbl_w = base_draw.textlength(label, font=small_text_f)
            
            # Pembagian spasi horizontal (35px) agar pas berjejer rapi di lebar 1080px
            start_x += num_w + lbl_w + 35

        # 8. Proses Pengiriman Buffer Memori
        output_buffer = BytesIO()
        output_buffer.name = "tweet_mobile_fixed.png"
        base.save(output_buffer, "PNG")
        output_buffer.seek(0)

        await inf_msg.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output_buffer,
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else message.id
        )

    except Exception as e:
        logger.error(f"Tweet Error: {e}")
        await inf_msg.edit(f"❌ <b>Gagal:</b> <code>{e}</code>")
      
