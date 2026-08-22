import re
from math import ceil
from typing import List, Optional, Tuple
from uuid import uuid4

from pyrogram import enums
from pyrogram.errors import QueryIdInvalid, RPCError
from pyrogram.helpers import kb
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from clients import session
from database import dB, state
from logs import logger


COLUMN_SIZE = 4
NUM_COLUMNS = 2


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        if not isinstance(other, InlineKeyboardButton):
            return NotImplemented
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n, module_dict, prefix, is_bot=False):
    modules = sorted(
        [
            EqInlineKeyboardButton(
                x["module"].__MODULES__,
                callback_data="{}_module({},{})".format(
                    prefix,
                    x["module"].__MODULES__.lower(),
                    page_n,
                ),
            )
            for x in module_dict.values()
            if hasattr(x["module"], "__MODULES__")
        ]
    )

    pairs = [
        modules[i:i + NUM_COLUMNS]
        for i in range(0, len(modules), NUM_COLUMNS)
    ]

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if pairs else 1
    modulo_page = page_n % max_num_pages

    if is_bot:
        if len(pairs) > COLUMN_SIZE:
            pairs = pairs[
                modulo_page * COLUMN_SIZE:
                COLUMN_SIZE * (modulo_page + 1)
            ]

            pairs.append(
                [
                    EqInlineKeyboardButton(
                        "⬅️",
                        callback_data="{}_prev({})".format(
                            prefix,
                            modulo_page - 1
                            if modulo_page > 0
                            else max_num_pages - 1,
                        ),
                    ),
                    EqInlineKeyboardButton(
                        "❌",
                        callback_data="buttonclose",
                    ),
                    EqInlineKeyboardButton(
                        "➡️",
                        callback_data="{}_next({})".format(
                            prefix,
                            modulo_page + 1,
                        ),
                    ),
                ]
            )
        else:
            pairs.append(
                [
                    EqInlineKeyboardButton(
                        "🔙 Back",
                        callback_data="{}_help_back({})".format(
                            prefix,
                            page_n,
                        ),
                    )
                ]
            )

    else:
        if len(pairs) > COLUMN_SIZE:
            pairs = pairs[
                modulo_page * COLUMN_SIZE:
                COLUMN_SIZE * (modulo_page + 1)
            ]

            pairs.append(
                [
                    EqInlineKeyboardButton(
                        "⬅️",
                        callback_data="{}_prev({})".format(
                            prefix,
                            modulo_page - 1
                            if modulo_page > 0
                            else max_num_pages - 1,
                        ),
                    ),
                    EqInlineKeyboardButton(
                        "❌",
                        callback_data="close help",
                    ),
                    EqInlineKeyboardButton(
                        "➡️",
                        callback_data="{}_next({})".format(
                            prefix,
                            modulo_page + 1,
                        ),
                    ),
                ]
            )
        else:
            pairs.append(
                [
                    EqInlineKeyboardButton(
                        "🔙 Back",
                        callback_data="{}_help_back({})".format(
                            prefix,
                            page_n,
                        ),
                    )
                ]
            )

    return pairs


class ButtonUtils:

    URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?"
        r"[a-zA-Z0-9.-]+"
        r"(?:\.[a-zA-Z]{2,})+"
        r"(?:[/?]\S+)?|tg://\S+"
    )

    BUTTON_PATTERN = re.compile(r"\[(.*?)\|(.*?)\]")

    FORMAT_TAGS = {
        "<b>": "**",
        "<i>": "__",
        "<strike>": "~~",
        "<spoiler>": "||",
        "<u>": "--",
    }

    # =========================================================
    # BUTTON HELPER
    # =========================================================

    @staticmethod
    def make_button(
        text: str,
        callback_data: Optional[str] = None,
        *,
        url: Optional[str] = None,
        user_id: Optional[int] = None,
        copy_text: Optional[str] = None,
        style=None,
    ) -> InlineKeyboardButton:

        kwargs = {
            "text": text,
        }

        if callback_data is not None:
            kwargs["callback_data"] = callback_data

        if url is not None:
            kwargs["url"] = url

        if user_id is not None:
            kwargs["user_id"] = user_id

        if copy_text is not None:
            kwargs["copy_text"] = copy_text

        if style is not None:
            kwargs["style"] = style

        return InlineKeyboardButton(**kwargs)

    # =========================================================
    # CHECK URL
    # =========================================================

    @staticmethod
    def is_url(text: str) -> bool:
        return bool(re.search(ButtonUtils.URL_PATTERN, text))

    # =========================================================
    # CHECK NUMBER
    # =========================================================

    @staticmethod
    def is_number(text: str) -> bool:
        return text.isdigit()

    # =========================================================
    # CHECK COPY
    # =========================================================

    @staticmethod
    def is_copy(text: str) -> bool:
        return bool(re.search(r"copy:", text))

    # =========================================================
    # CHECK ALERT
    # =========================================================

    @staticmethod
    def is_alert(text: str) -> bool:
        return bool(re.search(r"alert:", text))

    # =========================================================
    # CHECK WEB
    # =========================================================

    @staticmethod
    def is_web(text: str) -> bool:
        return bool(re.search(r"web:", text))

    # =========================================================
    # CHECK CATBOX
    # =========================================================

    @staticmethod
    def cek_tg(text):

        tg_pattern = r"https?:\/\/files\.catbox\.moe\/\S+"
        match = re.search(tg_pattern, text)

        if match:
            tg_link = match.group(0)
            non_tg_text = text.replace(
                tg_link,
                "",
            ).strip()

            return tg_link, non_tg_text

        return None, text

    # =========================================================
    # PARSE BUTTON
    # =========================================================

    @staticmethod
    def parse_msg_buttons(
        texts: str,
    ) -> Tuple[str, List[List]]:

        btn = []

        for z in ButtonUtils.BUTTON_PATTERN.findall(texts):

            text, url = z

            urls = url.split("|")
            url = urls[0]

            if len(urls) > 1:
                btn[-1].append(
                    [text, url]
                )
            else:
                btn.append(
                    [[text, url]]
                )

        txt = texts

        for z in re.findall(
            r"\[.+?\|.+?\]",
            texts,
        ):
            txt = txt.replace(
                z,
                "",
            )

        return txt.strip(), btn

    # =========================================================
    # CREATE BUTTON
    # =========================================================

    @staticmethod
    async def create_button(
        text: str,
        data: str,
        with_suffix: str = "",
    ) -> InlineKeyboardButton:

        data = data.strip()

        if ButtonUtils.is_url(data):

            return ButtonUtils.make_button(
                text,
                url=data,
            )

        elif ButtonUtils.is_number(data):

            return ButtonUtils.make_button(
                text,
                user_id=int(data),
            )

        elif ButtonUtils.is_copy(data):

            return ButtonUtils.make_button(
                text,
                copy_text=data.replace(
                    "copy:",
                    "",
                ),
            )

        elif ButtonUtils.is_alert(data):

            alert_text = data.replace(
                "alert:",
                "",
            )

            uniq = str(uuid4().int)[:8]

            await dB.set_var(
                int(uniq),
                int(uniq),
                alert_text,
            )

            cb_data = f"alertcb_{int(uniq)}"

            return ButtonUtils.make_button(
                text,
                callback_data=cb_data,
                style=enums.ButtonStyle.PRIMARY,
            )

        callback = (
            f"{data}_{with_suffix}"
            if with_suffix
            else data
        )

        return ButtonUtils.make_button(
            text,
            callback_data=callback,
            style=enums.ButtonStyle.PRIMARY,
        )

    # =========================================================
    # CREATE INLINE KEYBOARD
    # =========================================================

    @staticmethod
    async def create_inline_keyboard(
        buttons: List[List],
        suffix: str = "",
    ) -> InlineKeyboardMarkup:

        keyboard = []

        for row in buttons:

            keyboard.append(
                [
                    await ButtonUtils.create_button(
                        text,
                        data,
                        suffix,
                    )
                    for text, data in row
                ]
            )

        return InlineKeyboardMarkup(keyboard)

    # =========================================================
    # START MENU
    # =========================================================

    @staticmethod
    def start_menu(user_id: int) -> kb:

        if not session.get_session(user_id):

            common_buttons = [
                ["✨ Mulai Buat Userbot"],
                ["❓ Status Akun"],
                [
                    ("⚡ Plan Lite"),
                    ("🧩 Plan Basic"),
                    ("💎 Plan Pro"),
                ],
                ["💬 Hubungi Admins"],
                ["🔑 Token"],
            ]

        else:

            common_buttons = [
                ["❓ Status Akun"],
                ["🔑 Token"],
                [
                    ("🔄 Reset Emoji"),
                    ("🔄 Reset Prefix"),
                ],
                [
                    ("🔄 Restart Userbot"),
                    ("🔄 Reset Text"),
                ],
                ["💬 Hubungi Admins"],
            ]

        return kb(
            common_buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    # =========================================================
    # USERBOT LIST
    # =========================================================

    @staticmethod
    def userbot_list(
        user_id,
        count,
        total_count,
    ):

        buttons = []
        nav_buttons = []

        if count > 0:

            nav_buttons.append(
                ButtonUtils.make_button(
                    "❮",
                    callback_data=f"prev_ub {count}",
                    style=enums.ButtonStyle.PRIMARY,
                )
            )

        page_number = (count // 10) * 10

        nav_buttons.append(
            ButtonUtils.make_button(
                "Kembali",
                callback_data=f"bcpg_acc {page_number}",
                style=enums.ButtonStyle.PRIMARY,
            )
        )

        if count < total_count - 1:

            nav_buttons.append(
                ButtonUtils.make_button(
                    "❯",
                    callback_data=f"next_ub {count}",
                    style=enums.ButtonStyle.PRIMARY,
                )
            )

        buttons.append(nav_buttons)

        action_buttons = [
            [
                ButtonUtils.make_button(
                    "Get OTP",
                    callback_data=f"get_otp {count}",
                    style=enums.ButtonStyle.SUCCESS,
                )
            ],
            [
                ButtonUtils.make_button(
                    "Hapus User",
                    callback_data=f"del_ubot {user_id}",
                    style=enums.ButtonStyle.DANGER,
                ),
                ButtonUtils.make_button(
                    "Hapus Akun",
                    callback_data=f"ub_deak {count}",
                    style=enums.ButtonStyle.DANGER,
                ),
            ],
        ]

        buttons.extend(action_buttons)

        return InlineKeyboardMarkup(buttons)

    # =========================================================
    # ACCOUNT LIST
    # =========================================================

    @staticmethod
    def account_list(start_index=0):

        user_list = session.get_list()
        total_users = len(user_list)

        buttons = []
        row = []

        end_index = min(
            start_index + 10,
            total_users,
        )

        for i in range(
            start_index,
            end_index,
        ):

            user_id = user_list[i]

            button = ButtonUtils.make_button(
                f"{i + 1}",
                callback_data=f"tools_acc {user_id}-{i}",
                style=enums.ButtonStyle.PRIMARY,
            )

            row.append(button)

            if len(row) == 5:

                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        nav_buttons = []

        if start_index > 0:

            nav_buttons.append(
                ButtonUtils.make_button(
                    "◀️ Prev page",
                    callback_data=f"acc_page {start_index - 10}",
                    style=enums.ButtonStyle.PRIMARY,
                )
            )

        if end_index < total_users:

            nav_buttons.append(
                ButtonUtils.make_button(
                    "Next page ▶️",
                    callback_data=f"acc_page {end_index}",
                    style=enums.ButtonStyle.PRIMARY,
                )
            )

        if nav_buttons:
            buttons.append(nav_buttons)

        buttons.append(
            [
                ButtonUtils.make_button(
                    "Tutup",
                    callback_data="buttonclose",
                    style=enums.ButtonStyle.DANGER,
                )
            ]
        )

        return InlineKeyboardMarkup(buttons)

    # =========================================================
    # DEACTIVATE
    # =========================================================

    @staticmethod
    def deak(
        user_id,
        count,
    ):

        return InlineKeyboardMarkup(
            [
                [
                    ButtonUtils.make_button(
                        "⬅️",
                        callback_data=f"prev_ub {int(count)}",
                        style=enums.ButtonStyle.PRIMARY,
                    ),
                    ButtonUtils.make_button(
                        "Approve",
                        callback_data=f"deak_akun {int(count)}",
                        style=enums.ButtonStyle.SUCCESS,
                    ),
                ]
            ]
        )

    # =========================================================
    # INLINE QUERY
    # =========================================================

    @staticmethod
    async def generate_inline_query(
        message,
        chat_id,
        bot_username,
        query,
    ):

        try:

            client = message._client

            results = await client.get_inline_bot_results(
                bot_username,
                query,
            )

            if results and results.results:

                return {
                    "query_id": results.query_id,
                    "result_id": results.results[0].id,
                    "results": results.results,
                    "query": query,
                }

            return None

        except Exception:
            return None

    # =========================================================
    # SEND INLINE BOT RESULT
    # =========================================================

    @staticmethod
    async def send_inline_bot_result(
        message,
        chat_id,
        bot_username,
        query,
        reply_to_message_id: Optional[int] = None,
    ) -> bool:

        client = message._client

        try:

            query_results = await ButtonUtils.generate_inline_query(
                message,
                chat_id,
                bot_username,
                query,
            )

            if not query_results:
                return False

            data = await client.send_inline_bot_result(
                chat_id,
                query_results["query_id"],
                query_results["result_id"],
                reply_to_message_id=reply_to_message_id,
                message_thread_id=(
                    message.message_thread_id
                    or None
                ),
            )

            inline_id = {
                "chat": chat_id,
                "_id": data.updates[0].id,
                "me": client.me.id,
                "idm": id(message),
            }

            state.set(
                query,
                query,
                inline_id,
            )

            logger.info(
                f"Inline query '{query}'"
            )

            return True

        except RPCError:
            raise

        except QueryIdInvalid:
            raise

        except Exception:
            raise

    # =========================================================
    # BUILD BUTTONS
    # =========================================================

    @staticmethod
    def build_buttons(
        data,
        uniq,
        callback,
        closed,
    ):

        buttons = []
        row = []

        for idx, _ in enumerate(data):

            row.append(
                ButtonUtils.make_button(
                    str(idx + 1),
                    callback_data=f"{callback}{idx}_{uniq}",
                    style=enums.ButtonStyle.PRIMARY,
                )
            )

            if len(row) == 5:

                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        buttons.append(
            [
                ButtonUtils.make_button(
                    "❌ Close",
                    callback_data=f"close {closed} {uniq}",
                    style=enums.ButtonStyle.DANGER,
                )
            ]
        )

        return InlineKeyboardMarkup(buttons)

    # =========================================================
    # PLUS / MINUS
    # =========================================================

    @staticmethod
    def plus_minus(
        bulan,
        harga,
        plan,
    ):

        return InlineKeyboardMarkup(
            [
                [
                    ButtonUtils.make_button(
                        "⁻1 bulan",
                        callback_data=f"kurang {bulan} {harga} {plan}",
                        style=enums.ButtonStyle.DANGER,
                    ),
                    ButtonUtils.make_button(
                        "⁺1 bulan",
                        callback_data=f"tambah {bulan} {harga} {plan}",
                        style=enums.ButtonStyle.SUCCESS,
                    ),
                ],
                [
                    ButtonUtils.make_button(
                        "Konfirmasi",
                        callback_data=f"confirm {bulan} {harga} {plan}",
                        style=enums.ButtonStyle.SUCCESS,
                    )
                ],
                [
                    ButtonUtils.make_button(
                        "Batal",
                        callback_data="buttonclose",
                        style=enums.ButtonStyle.DANGER,
                    )
                ],
            ]
        )

    # =========================================================
    # CHOOSE PLAN
    # =========================================================

    @staticmethod
    def chose_plan():

        return InlineKeyboardMarkup(
            [
                [
                    ButtonUtils.make_button(
                        "🧩 Plan Basic",
                        callback_data="planusers basic",
                        style=enums.ButtonStyle.PRIMARY,
                    ),
                    ButtonUtils.make_button(
                        "💎 Plan Pro",
                        callback_data="planusers is_pro",
                        style=enums.ButtonStyle.SUCCESS,
                    ),
                ],
                [
                    ButtonUtils.make_button(
                        "⚡ Plan Lite",
                        callback_data="planusers lite",
                        style=enums.ButtonStyle.PRIMARY,
                    )
                ],
                [
                    ButtonUtils.make_button(
                        "Batal",
                        callback_data="buttonclose",
                        style=enums.ButtonStyle.DANGER,
                    )
                ],
            ]
        )

    # =========================================================
    # FONT KEYBOARD
    # =========================================================

    @staticmethod
    def create_font_keyboard(
        font_list,
        get_id,
        current_batch,
    ):

        keyboard = []

        for font_dict in font_list:

            for key, value in font_dict.items():

                keyboard.append(
                    ButtonUtils.make_button(
                        key,
                        callback_data=f"get_font {get_id} {value}",
                        style=enums.ButtonStyle.PRIMARY,
                    )
                )

        rows = [
            keyboard[i:i + 2]
            for i in range(
                0,
                len(keyboard),
                2,
            )
        ]

        while len(rows) < 3:
            rows.append([])

        rows.append(
            [
                ButtonUtils.make_button(
                    "⬅️",
                    callback_data=f"prev_font {get_id} {current_batch}",
                    style=enums.ButtonStyle.PRIMARY,
                ),
                ButtonUtils.make_button(
                    "❌",
                    callback_data=f"close inline_font {get_id}",
                    style=enums.ButtonStyle.DANGER,
                ),
                ButtonUtils.make_button(
                    "➡️",
                    callback_data=f"next_font {get_id} {current_batch}",
                    style=enums.ButtonStyle.PRIMARY,
                ),
            ]
        )

        return InlineKeyboardMarkup(rows)
