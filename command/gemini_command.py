import traceback

import config
from helpers import Emoji, Tools, animate_proses
from logs import logger



async def gemini_cmd(client, message):
    em = Emoji(client)
    await em.get()
    proses = await animate_proses(message, em.proses)

    if len(message.command) < 2:
        return await proses.edit(
            f"{em.gagal}**Please give a question or reply with an image and question.**"
        )
    prompt = message.text.split(None, 1)[1]
    try:
        headers = {
            "x-maelyn-auth": config.API_MAELYN,
            "Content-Type": "application/json",
        }

        if len(message.command) < 2:
            return await proses.edit(
                f"{em.gagal}**Please provide a question to analyze the image.**"
            )

        params = {
            "prompt": prompt,
            "model": "gemini-3-flash-preview"
        }
        r = await Tools.fetch.get("https://api.maelyn.eu/api/ai/gemini", headers=headers, params=params)
        if r.status_code != 200:
            return await proses.edit(
                f"<b>Please try again later: {r.status_code}</b>"
            )
        data = r.json()
        return await proses.edit(data.get("result"))
    except Exception as e:
        logger.error(traceback.format_exc())
        return await proses.edit(f"{em.gagal}**Terjadi kesalahan:**\n`{e}`")
