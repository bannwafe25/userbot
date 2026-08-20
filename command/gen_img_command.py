import os
import re
import shutil
import traceback
import uuid

import aiofiles
import aiohttp
from pyrogram.types import InputMediaPhoto
from pyrogram import Client
from pyrogram.types import Message

from config import API_MAELYN
from helpers import Bing, Emoji, Tools, animate_proses
from logs import logger



async def quote_cmd(client: Client, message: Message):
    em = Emoji(client)
    await em.get()

    reply = message.reply_to_message
    if not reply:
        await message.edit_text(
            f"{em.gagal} Silakan *reply* ke pesan yang ingin dijadikan Quotly."
        )
        return

    # Custom background color
    bg_color = "#1b1429"
    if len(message.command) > 1:
        bg_color = message.command[1]

    progress = await message.edit_text(
        f"{em.proses} Sedang merender Quotly..."
    )

    try:
        # 1. Data user target
        user = reply.from_user or reply.sender_chat

        user_id = user.id if user else 1
        first_name = (
            user.first_name
            if hasattr(user, "first_name") and user.first_name
            else (user.title or "User")
        )
        last_name = (
            user.last_name
            if hasattr(user, "last_name") and user.last_name
            else ""
        )
        username = (
            user.username
            if hasattr(user, "username") and user.username
            else ""
        )

        # 2. Foto profil
        avatar_url = (
            f"https://ui-avatars.com/api/?name={first_name.replace(' ', '+')}"
            "&background=random"
        )

        if user and hasattr(user, "photo") and user.photo:
            try:
                photo_bytes = await client.download_media(
                    user.photo.big_file_id,
                    in_memory=True
                )

                if photo_bytes:
                    avatar_url = (
                        "data:image/jpeg;base64,"
                        f"{base64.b64encode(photo_bytes.getvalue()).decode()}"
                    )

            except Exception:
                pass

        text_content = reply.text or reply.caption or ""

        # 3. Data pengirim
        from_data = {
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "photo": {
                "url": avatar_url
            }
        }

        # 4. Reply message
        reply_message_data = None

        if reply.reply_to_message:
            r_msg = reply.reply_to_message
            r_user = r_msg.from_user or r_msg.sender_chat

            r_id = r_user.id if r_user else 123456789

            r_fname = (
                r_user.first_name
                if hasattr(r_user, "first_name") and r_user.first_name
                else (r_user.title or "User")
            )

            r_lname = (
                r_user.last_name
                if hasattr(r_user, "last_name") and r_user.last_name
                else ""
            )

            reply_message_data = {
                "name": f"{r_fname} {r_lname}".strip(),
                "text": r_msg.text or r_msg.caption or "🖼 Media",
                "entities": [],
                "chatId": r_id,
                "from": {
                    "id": r_id,
                    "name": f"{r_fname} {r_lname}".strip(),
                    "photo": {
                        "url": (
                            "https://ui-avatars.com/api/?name="
                            f"{r_fname.replace(' ', '+')}"
                            "&background=random"
                        )
                    }
                }
            }

        message_object = {
            "from": from_data,
            "text": text_content,
            "entities": [],
            "avatar": True
        }

        if reply_message_data:
            message_object["replyMessage"] = reply_message_data

        # 5. Payload
        payload = {
            "backgroundColor": bg_color,
            "width": 512,
            "height": 768,
            "scale": 2,
            "emojiBrand": "apple",
            "messages": [
                message_object
            ]
        }

        # 6. Generate
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        async with httpx.AsyncClient(timeout=25.0) as http_client:
            response = await http_client.post(
                "https://quote.yuri.ly/generate.webp",
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            await progress.edit_text(
                f"{em.gagal} API Error ({response.status_code}):\n"
                f"`{response.text[:100]}`"
            )
            return

        sticker_data = BytesIO(response.content)
        sticker_data.name = "quotly.webp"

        await message.reply_sticker(
            sticker=sticker_data
        )

        await progress.delete()

    except Exception as e:
        await progress.edit_text(
            f"{em.gagal} Terjadi kesalahan:\n`{e}`"
        )

async def gen_studio(folder_name, prompt):
    prompt_clean = re.sub(r"[^\x20-\x7E]", "", prompt.strip())

    try:
        os.makedirs(folder_name, exist_ok=True)

        url = f"https://api.siputzx.my.id/api/ai/flux?prompt={prompt_clean}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200 and response.content_type == "image/png":
                    file_path = os.path.join(folder_name, "flux_1.png")
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(await response.read())

                    files = [
                        os.path.join(folder_name, f)
                        for f in os.listdir(folder_name)
                        if f.endswith(".png")
                    ]

                    return folder_name, files
                else:
                    text = await response.text()
                    logger.error(f"Flux API error {response.status}: {text}")
                    return folder_name, []

    except Exception:
        logger.error(f"gen_flux error: {traceback.format_exc()}")
        return folder_name, []

async def brat_cmd(client, message):
    em = Emoji(client)
    await em.get()

    command = message.command[0]
    is_video = command != "brat"
    prompt = client.get_text(message)

    if not prompt:
        return await message.reply(
            f"{em.gagal}**Please reply to a message containing the prompt!**\n"
            f"Example: `{command} aku ganteng`"
        )

    proses = await animate_proses(message, em.proses)

    try:
        response = await Tools.fetch.get(
            "https://api.maelyn.eu/api/canvas/brat",
            headers={
                "x-maelyn-auth": "sk_ms_2e9541fd10b7f6f7a7e6c5ac24aa4d407c4ea02fa1a58854"
            },
            params={
                "text": prompt,
                "isvideo": str(is_video).lower(),
                "speed": "fast"
            }
        )

        data = response.json()

        if not data.get("success"):
            raise Exception(data.get("message", "Unknown error"))

        file_url = data["result"]["url"]
        file_type = data["result"]["type"]

        media = await Tools.fetch.get(file_url)

        ext = "gif" if file_type == "gif" else "webp"
        file_path = f"brat_{uuid.uuid4().hex}.{ext}"

        with open(file_path, "wb") as f:
            f.write(media.content)

        if is_video:
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                caption=f"{em.sukses}**Generated by {client.me.mention}**",
                supports_streaming=True,
            )
        else:
            await client.send_sticker(
                chat_id=message.chat.id,
                sticker=file_path,
            )

        os.remove(file_path)
        await proses.delete()

    except Exception as e:
        await proses.edit(f"{em.gagal}**ERROR:**\n{e}")


async def bingai_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    prompt = client.get_text(message)

    if not prompt:
        return await message.reply(
            f"{emo.gagal}<b>Give the query you want to make!\n\nExample: \n<code>{message.text.split()[0]} Gambarkan lelaki Jepang tampan sedang duduk di bangku, mengenakan hoodie hitam dengan tulisan 'Kynan only Me' di bagian depan dan kacamata, sambil menghisap rokok dengan sikap santai. Latar belakang menampilkan hutan hujan yang rimbun, dengan cahaya lembut yang menerobos di antara dedaunan, menciptakan suasana tenang dan memikat. Tambahkan efek asap rokok yang melayang di udara, memberikan nuansa misterius pada gambar. Kualitas gambar harus tinggi (4k) dengan detail yang tajam dan warna alami yang kaya || Hindari elemen yang terlalu cerah, ekspresi wajah yang berlebihan, dan latar belakang yang terlalu ramai yang dapat mengalihkan perhatian dari sosok utama.</code></b>"
        )
    pros = await message.reply(
        f"{emo.proses}<b>Proses generate <code>{prompt}</code> ..</b>"
    )
    folder_name = f"downloads/{client.me.id}/"
    try:
        folder_name, imgs = await Bing.generate_images(folder_name, prompt)
        if imgs:
            media_group = []
            for img in imgs:
                if os.path.exists(img):
                    caption = f"{emo.sukses}<b>Successfully generate image:</b>"
                    media_group.append(InputMediaPhoto(media=img, caption=caption))

            if media_group:
                await client.send_media_group(
                    chat_id=message.chat.id,
                    media=media_group,
                    reply_to_message_id=message.id,
                )

            await pros.delete()

            if folder_name:
                shutil.rmtree(folder_name)
            for img in imgs:
                if os.path.exists(img):
                    os.remove(img)
        else:
            return await pros.edit(
                f"{emo.gagal}<b>Images are not found or failed generate images.</b>"
            )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Bing error: {traceback.format_exc()}")
        if "Failed to decode" in error_message:
            return await pros.edit(
                f"{emo.gagal}<b>Failed generate image.Please repeat again...</b>"
            )
        else:
            return await pros.edit(
                f"{emo.gagal}<b>Error:</b>\n <code>{error_message}</code>"
            )
    return


async def maker_img_cmd(client, message):
    em = Emoji(client)
    await em.get()
    if len(message.command) < 2:
        return await message.reply(
            f"{em.gagal}**Please give me command and reply to photo!!\nExample: `{message.text.split()[0]} nude` (reply photo).**"
        )
    proses = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    if message.command[1] == "sertifikat":
        if len(message.command) < 3:
            return await proses.edit(
                f"{em.gagal}**Please give text!!\nExample: `{message.text.split()[0]} sertifikat anak babi`.**"
            )
        text = " ".join(message.command[2:])
        params = {"text": text}
        url = "https://api.siputzx.my.id/api/m/sertifikat-tolol"
        response = await Tools.fetch.post(url, json=params)
        if response.status_code == 200:
            if not response.content:
                return await proses.edit(f"{em.gagal}**Please try again.**")
            file_path = f"sertifikat_{uuid.uuid4().hex}.jpg"
            with open(file_path, "wb") as f:
                f.write(response.content)
            await message.reply_photo(
                file_path, caption=f"{em.sukses}<b>Succesfully generate image.</b>"
            )
            os.remove(file_path)
            return await proses.delete()
        else:
            return await proses.edit(
                f"{em.gagal}<b>Failed to generate image. Please try again later.</b>"
            )
    elif message.command[1] == "xnxx":
        if len(message.command) < 3:
            return await proses.edit(
                f"{em.gagal}**Please give text!!\nExample: `{message.text.split()[0]} xnxx skandal viral`.**"
            )
        text = " ".join(message.command[2:])
        if not message.reply_to_message.media:
            return await proses.edit(f"{em.gagal}**Please reply photo!!**")
        media = await reply.download()
        async with aiofiles.open(media, mode="rb") as file:
            file_data = await file.read()
        url = "https://api.siputzx.my.id/api/canvas/xnxx"
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("title", text)
            form.add_field(
                "image", file_data, filename="image.jpg", content_type="image/jpeg"
            )

            async with session.post(url, data=form) as response:
                if response.status != 200:
                    return await proses.edit(f"{em.gagal}**Please try again later!!**")
                file_path = f"canvas{uuid.uuid4().hex}.jpg"
                with open(file_path, "wb") as f:
                    f.write(await response.read())
                await proses.delete()
                return await message.reply_photo(file_path)
    else:
        return await proses.edit(
            f"{em.gagal}**Please give me command and reply to photo!!\nExample: `{message.text.split()[0]} nude` (reply photo).**"
        )


async def dalle_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)
    prompt = client.get_text(message)
    if not prompt:
        return await proses.edit(
            f"{em.gagal}**Please reply to a message containing the prompt!\n"
            f"Example: `{message.text.split()[0]} beautiful japanese girl`**"
        )
    headers = {"mg-apikey": API_MAELYN}
    params = {"prompt": prompt, "resolution": "Square"}
    url = "https://api.maelyn.eu/api/ai/generate/v1/image"
    response = await Tools.fetch.get(url, headers=headers, params=params)
    if response.status_code == 200:
        try:
            data = response.json()["result"].get("url")
            img = await Tools.get_media_data(data, "jpg")
            caption = f"{em.sukses}<b>Successfully generate image.</b>"
            await message.reply_photo(img, caption=caption)
            return await proses.delete()
        except Exception:
            return await proses.edit(
                f"{em.gagal}<b>Failed to generate image. Please try again later.</b>"
            )
    else:
        return await proses.edit(
            f"{em.gagal}<b>Failed to generate image. Please try again later.</b>"
        )


async def startnest_cmd(client, message):
    em = Emoji(client)
    await em.get()
    text = client.get_text(message)
    if not text:
        return await message.reply(
            f"{em.gagal} **Please reply to message text or give message!\nExample: `{message.text.split()[0]} beautiful girl`.**"
        )
    pros = await animate_proses(message, em.proses)
    try:
        url = f"https://api.maelyn.sbs/api/txt2img/startnest?prompt={text}&apikey={API_MAELYN}"
        result = await Tools.fetch.get(url)
        if result.status_code == 200:
            image = result.json()["result"][0]
            await message.reply_photo(image)
            return await pros.delete()
        else:
            return await pros.edit(f"{em.gagal}**ERROR:**{result.status_code}")
    except Exception as e:
        await message.reply(f"{em.gagal}**ERROR:** {str(e)}")
        return await pros.delete()

async def remini_cmd(client, message):
    em = Emoji(client)
    await em.get()

    prs = await animate_proses(message, em.proses)
    rep = message.reply_to_message

    try:
        if rep and rep.media:
            image_url = await Tools.maelyn_upload(rep)
        else:
            image_url = client.get_text(message)

            if not image_url:
                return await prs.edit(
                    f"{em.gagal}**Please reply to image or give link.!!**"
                )

            if not image_url.startswith(("http://", "https://")):
                return await prs.edit(
                    f"{em.gagal}**Please give valid link or reply media**"
                )

        await prs.edit(f"{em.proses}**Scanning of image...**")

        respon = await Tools.fetch.post(
            "https://api.maelyn.eu/api/ai/image/hd",
            headers={
                "x-maelyn-auth": "sk_ms_2e9541fd10b7f6f7a7e6c5ac24aa4d407c4ea02fa1a58854",
                "Content-Type": "application/json"
            },
            json={
                "image_url": image_url
            }
        )

        data = respon.json()

        if respon.status_code != 200 or not data.get("success"):
            return await prs.edit(
                f"{em.gagal}**ERROR:**\n{data.get('message', 'Upscale failed')}"
            )

        result = data["result"]
        url = result.get("url")
        size = result.get("size", "-")

        await prs.delete()

        return await message.reply_photo(
            url,
            caption=(
                f"{em.sukses}**Image HD Success**\n"
                f"**Size**: {size}"
            )
        )

    except Exception as er:
        await prs.delete()
        return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")

async def genai_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)
    prompt = client.get_text(message)
    if not prompt:
        return await proses.edit(
            f"{em.gagal}**Please reply to a message containing the prompt!\n"
            f"Example: `{message.text.split()[0]} beautiful japanese girl`**"
        )
    try:
        url = f"https://api.maelyn.eu/api/ai/ai/generate/v1/image/realistic?prompt={prompt}&resolution=Portrait&apikey={API_MAELYN}"
        result = await Tools.fetch.get(url)
        if result.status_code != 200:
            return await proses.edit(f"{em.gagal}**Please try again later!!**")
        data = result.json().get("result", [])
        if not data:
            return await proses.edit(f"{em.gagal}**No image found!!**")
        image = data[0]
        await message.reply_photo(image)
        return await proses.delete()
    except Exception as e:
        await message.reply(f"{em.gagal}**ERROR:** {str(e)}")
        return await proses.delete()


