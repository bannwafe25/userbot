"""
Shim Client.ask() untuk kurigram (2.2.26 tidak punya method ask/listener).
Implementasi minimal: kirim pesan prompt (dengan reply_markup bila ada),
lalu tunggu balasan berikutnya dari chat yang sama via MessageHandler sementara.
"""
import asyncio
import pyrogram
from pyrogram import filters
from pyrogram.handlers import MessageHandler

import logging
logger = logging.getLogger("ask_shim")


def install_ask_shim():
    if hasattr(pyrogram.Client, "ask"):
        return

    async def ask(
        self,
        chat_id,
        text,
        filters=None,
        user_id=None,
        timeout=None,
        *args,
        **kwargs,
    ):
        await self.send_message(chat_id, text, **kwargs)

        fut = asyncio.get_event_loop().create_future()

        flt = filters if filters is not None else pyrogram.filters.all

        async def _handler(client, message):
            logger.info(f"[ask_shim] pesan masuk dari {message.chat.id}: {type(message).__name__}")
            if not fut.done():
                fut.set_result(message)

        h = MessageHandler(_handler, flt & pyrogram.filters.chat(chat_id))
        self.add_handler(h, group=-100)
        logger.info(f"[ask_shim] listener terpasang, nunggu balasan dari {chat_id}")

        try:
            if timeout:
                return await asyncio.wait_for(fut, timeout)
            return await asyncio.wait_for(fut, timeout=300)
        except asyncio.TimeoutError:
            logger.warning("[ask_shim] TIMEOUT nunggu balasan")
            raise TimeoutError("ask timeout")
        finally:
            try:
                self.remove_handler(h, group=-100)
            except Exception:
                pass

    pyrogram.Client.ask = ask
