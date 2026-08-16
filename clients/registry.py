python3 -c "code = '''import asyncio
import traceback
from datetime import datetime
from pyrogram import errors
from pyrogram.handlers import MessageHandler
from config import config
from helpers import Emoji

class HandlerRegistry:
    @classmethod
    def _create_wrapped_handler(cls, original_func):
        async def wrapped_handler(client, message):
            try:
                if asyncio.iscoroutinefunction(original_func):
                    await original_func(client, message)
                else:
                    original_func(client, message)
            except (
                errors.FloodWait,
                errors.FloodPremiumWait,
                errors.SlowmodeWait,
            ) as e:
                await asyncio.sleep(e.value)
                await original_func(client, message)
            except (
                errors.ChatWriteForbidden,
                errors.ChatSendMediaForbidden,
                errors.ChatSendPhotosForbidden,
                errors.MessageNotModified,
                errors.MessageIdInvalid,
                errors.ChatSendPlainForbidden,
                errors.AuthKeyUnregistered,
            ):
                pass
            except errors.PremiumAccountRequired:
                em = Emoji(client)
                await em.reset_emoji()
                return await original_func(client, message)
            except Exception as e:
                date_time = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")
                user_id = message.from_user.id if message.from_user else \"Unknown\"
                chat_id = message.chat.id if message.chat else \"Unknown\"
                chat_username = (
                    f\"@{message.chat.username}\"
                    if message.chat.username
                    else \"Private Group\"
                )
                command = message.text
                error_trace = traceback.format_exc()

                error_message = (
                    f\"<b>Error:</b> {type(e).__name__}\\n\"
                    f\"<b>Date:</b> {date_time}\\n\"
                    f\"<b>Chat ID:</b> {chat_id}\\n\"
                    f\"<b>Chat Username:</b> {chat_username}\\n\"
                    f\"<b>User ID:</b> {user_id}\\n\"
                    f\"<b>Command/Text:</b>\\n<pre language='python'><code>{command}</code></pre>\\n\"
                    f\"<b>Traceback:</b>\\n<pre><code>{error_trace}</code></pre>\"
                )
                try:
                    await client.send_message(config.LOG_BACKUP, error_message)
                except Exception:
                    pass

        return wrapped_handler

    @classmethod
    def add_message_handler(cls, cls_self, filters: Filter, original_func, group: int):
        wrapped_func = cls._create_wrapped_handler(original_func)
        return MessageHandler(wrapped_func, filters)
'''
open('clients/registry.py', 'w').write(code)
print('REGISTRY SYNCED FROM GITHUB!')"
