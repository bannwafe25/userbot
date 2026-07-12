from pyrogram import Client, filters
import random
from helpers import Emoji, CMD
from clients import navy

__MODULES__ = "CekDompet"
__HELP__ = """<blockquote>Command Help **Wikipedia**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **Search Wikipedia**
        `{0}dompet` (query)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True


def emoji(alias):
    emojis = {
        "DETEK": "<emoji id=6026321200597176575>🃏</emoji>",    
        "SUBJEK": "<emoji id=5382148180043376268>😱</emoji>",
        "DOMPET": "<emoji id=6257972409190585253>💰</emoji>",
        "ATM": "<emoji id=5472250091332993630>💳</emoji>",
        "DANA": "<emoji id=6161325517497701900>🤝</emoji>", 
        "ROYAL": "<emoji id=5384588885403641796>🥰</emoji>",
        "PELIT": "<emoji id=5384236096789949675>😒</emoji>",
        "MASAA": "<emoji id=5206659381151680254>☀️</emoji>",
        "ENERGY": "<emoji id=5215420556089776398>👛</emoji>",                   
    }
    return emojis.get(alias, "⎆")


dtk = emoji("DETEK")
subj = emoji("SUBJEK")
domp = emoji("DOMPET")
atm = emoji("ATM")
dana = emoji("DANA")
royal = emoji("ROYAL")
pelit = emoji("PELIT")
masaa = emoji("MASAA")
engy = emoji("ENERGY")


MASA_LIST = [
    "3 Hari",
    "5 Harii",
    "7 Hari",
    "9 Hari",
    "10 Hari",
    "12 Hari",
    "14 Hari",
    "16 Hari",
    "18 Hari",
    "20 Hari",
    "22 Hari",
    "24 Hari",
    "26 Hari",
    "28 Hari",
    "30 Hari",
    "Tidak Menentu",
    "Susah Ditebak",
]

ENERGY_STATUS_LIST = [
    "Stabil", 
    "Tidak Stabil", 
    "Sangat Kuat", 
    "Lemah Isi Dompetnya", 
    "Overload Bokeknya", 
    "Cepet Kosong", 
    "Banyak Cicilan",
]

@CMD.UBOT("dompet")
async def _(client, message, *args):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        user = await client.get_users(message.command[1])
    else:
        user = message.from_user
    
    if user:
        username = f"@{user.username}" if user.username else user.first_name
        dompet_percent = random.randint(10, 100)
        atm_percent = random.randint(10, 100)
        dana_percent = random.randint(10, 100)
        royal_percent = random.randint(10, 100)
        pelit_percent = random.randint(10, 100)        
        masa = random.choice(MASA_LIST)
        energy_status = random.choice(ENERGY_STATUS_LIST)

        response = f"""
<blockquote expandable>**__{dtk} **Deteksi Isi Dompet** {dtk}

{subj} **Subjek**: {username}
{domp} **Isi Dompet**: [{dompet_percent}%] {"█" * (dompet_percent // 10)}
{atm} **Saldo Atm**: [{atm_percent}%] {"█" * (atm_percent // 10)}
{dana} **Saldo Dana**: [{dana_percent}%] {"█" * (dana_percent // 10)}
{royal} **Jiwa Royal**: [{royal_percent}%] {"█" * (royal_percent // 10)}
{pelit} **Jiwa Pelit**: [{pelit_percent}%] {"█" * (pelit_percent // 10)}
{masaa} **Masa Bertahan**: {masa}

{engy} **Status Dompet**: {energy_status}__**</blockquote>
"""
        await message.reply_text(response)
    else:
        await message.reply_text("<blockquote >**Gagal mendeteksi pengguna...**</blockquote>")
