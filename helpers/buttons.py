import re
from math import ceil
from typing import List, Optional, Tuple
from uuid import uuid4

from pyrogram import enums
from pyrogram.errors import QueryIdInvalid, RPCError
from pyrogram.helpers import ikb, kb
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from clients import session
from database import dB, state
from logs import logger


COLUMN_SIZE = 4
NUM_COLUMNS = 2


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
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
        modules[i : i + NUM_COLUMNS]
        for i in range(0, len(modules), NUM_COLUMNS)
    ]

    max_num_pages = (
        ceil(len(pairs) / COLUMN_SIZE)
        if pairs
        else 1
    )

    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = (
            pairs[
                modulo_page * COLUMN_SIZE :
                COLUMN_SIZE * (modulo_page + 1)
            ]
            + [
                (
                    EqInlineKeyboardButton(
                        "⬅️",
                        callback_data="{}_prev({})".format(
                            prefix,
                            (
                                modulo_page - 1
                                if modulo_page > 0
                                else max_num_pages - 1
                            ),
                        ),
                    ),
                    EqInlineKeyboardButton(
                        "❌",
                        callback_data=(
                            "buttonclose"
                            if is_bot
                            else "close help"
                        ),
                    ),
                    EqInlineKeyboardButton(
                        "➡️",
                        callback_data="{}_next({})".format(
                            prefix,
                            modulo_page + 1,
                        ),
                    ),
                )
            ]
        )

    else:
        pairs.append(
            [
                EqInlineKeyboardButton(
                    "🔙 Back",
                    callback_data=(
                        f"{prefix}_help_back({page_n})"
                    ),
                )
            ]
        )

    return pairs


class ButtonUtils:

    # ============================================================
    # REGEX
    # ============================================================

    URL_PATTERN = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"[a-zA-Z0-9.-]+"
        r"(?:\.[a-zA-Z]{2,})+"
        r"(?:[/?]\S+)?"
        r"|tg://\S+"
    )

    # Support:
    #
    # [Text|callback]
    # [Text|callback|primary]
    # [Text|callback|success]
    # [Text|callback|danger]
    #
    BUTTON_PATTERN = re.compile(
        r"\[([^\[\]\r\n|]+)"
        r"\|([^\[\]\r\n|]+)"
        r"(?:\|([^\[\]\r\n|]+))?\]"
    )

    FORMAT_TAGS = {
        "<b>": "**",
        "<i>": "__",
        "<strike>": "~~",
        "<spoiler>": "||",
        "<u>": "--",
    }

    VALID_STYLES = {
        "primary",
        "success",
        "danger",
    }

    STYLE_MAP = {
        "primary": enums.ButtonStyle.PRIMARY,
        "success": enums.ButtonStyle.SUCCESS,
        "danger": enums.ButtonStyle.DANGER,
    }

    # ============================================================
    # BASIC CHECK
    # ============================================================

    @staticmethod
    def is_url(text: str) -> bool:
        """Check if text is a URL."""
        return bool(
            re.search(
                ButtonUtils.URL_PATTERN,
                text,
            )
        )

    @staticmethod
    def is_number(text: str) -> bool:
        """Check if text is a number."""
        return text.isdigit()

    @staticmethod
    def is_copy(text: str) -> bool:
        """Check if text is a copy button."""
        return bool(
            re.search(
                r"copy:",
                text,
            )
        )

    @staticmethod
    def is_alert(text: str) -> bool:
        """Check if text is an alert button."""
        return bool(
            re.search(
                r"alert:",
                text,
            )
        )

    @staticmethod
    def is_web(text: str) -> bool:
        """Check if text is a web button."""
        return bool(
            re.search(
                r"web:",
                text,
            )
        )

    # ============================================================
    # CATBOX
    # ============================================================

    @staticmethod
    def cek_tg(text):
        tg_pattern = r"https?:\/\/files\.catbox\.moe\/\S+"

        match = re.search(
            tg_pattern,
            text,
        )

        if match:
            tg_link = match.group(0)

            non_tg_text = text.replace(
                tg_link,
                "",
            ).strip()

            return tg_link, non_tg_text

        return None, text

    # ============================================================
    # PARSE BUTTONS
    # ============================================================

    @staticmethod
    def parse_msg_buttons(
        texts: str,
    ) -> Tuple[str, List[List]]:
        """
        Parse message buttons.

        Supported:

        [Button|callback]

        [Button|callback|primary]

        [Button|callback|success]

        [Button|callback|danger]

        Multiple buttons in one row:

        [Delete|delete|danger][Confirm|confirm|success]

        Different rows:

        [Delete|delete|danger]
        [Confirm|confirm|success]
        """

        buttons = []

        matches = list(
            ButtonUtils.BUTTON_PATTERN.finditer(texts)
        )

        if not matches:
            return texts.strip(), []

        current_row = []
        previous_end = None

        for match in matches:
            text = match.group(1).strip()
            data = match.group(2).strip()
            style = match.group(3)

            if style:
                style = style.strip().lower()

                if style not in ButtonUtils.VALID_STYLES:
                    logger.warning(
                        "Invalid button style '%s' "
                        "for '%s'. Using default.",
                        style,
                        text,
                    )
                    style = None

            # ----------------------------------------------------
            # Determine row
            # ----------------------------------------------------

            if previous_end is not None:
                between = texts[
                    previous_end : match.start()
                ]

                # New line = new row
                if "\n" in between:
                    if current_row:
                        buttons.append(
                            current_row
                        )

                    current_row = []

            # ----------------------------------------------------
            # Save button
            # ----------------------------------------------------

            if style:
                current_row.append(
                    [
                        text,
                        data,
                        style,
                    ]
                )
            else:
                current_row.append(
                    [
                        text,
                        data,
                    ]
                )

            previous_end = match.end()

        if current_row:
            buttons.append(
                current_row
            )

        # --------------------------------------------------------
        # Remove buttons from text
        # --------------------------------------------------------

        txt = ButtonUtils.BUTTON_PATTERN.sub(
            "",
            texts,
        )

        # Remove excessive blank lines
        txt = re.sub(
            r"\n[ \t]*\n+",
            "\n\n",
            txt,
        )

        return txt.strip(), buttons

    # ============================================================
    # STYLE HELPER
    # ============================================================

    @staticmethod
    def get_style(style: Optional[str]):
        """
        Convert style string into Pyrogram ButtonStyle.

        Supported:
            primary
            success
            danger
        """

        if not style:
            return None

        style = style.lower().strip()

        return ButtonUtils.STYLE_MAP.get(
            style
        )

    # ============================================================
    # STYLED INLINE BUTTON
    # ============================================================

    @staticmethod
    def styled_button(
        text: str,
        callback_data: str,
        style: Optional[str] = None,
    ) -> InlineKeyboardButton:
        """
        Create a styled inline callback button.

        Example:

        ButtonUtils.styled_button(
            "Confirm",
            "confirm",
            "success",
        )
        """

        kwargs = {
            "text": text,
            "callback_data": callback_data,
        }

        button_style = ButtonUtils.get_style(
            style
        )

        if button_style is not None:
            kwargs["style"] = button_style

        return InlineKeyboardButton(
            **kwargs
        )

    # ============================================================
    # CREATE BUTTON
    # ============================================================

    @staticmethod
    async def create_button(
        text: str,
        data: str,
        with_suffix: str = "",
        style: Optional[str] = None,
    ) -> InlineKeyboardButton:
        """
        Create an InlineKeyboardButton.

        Supports:
            URL
            user ID
            copy
            alert
            callback
            Telegram button style
        """

        data = data.strip()

        kwargs = {
            "text": text,
        }

        # --------------------------------------------------------
        # URL
        # --------------------------------------------------------

        if ButtonUtils.is_url(data):
            kwargs["url"] = data

        # --------------------------------------------------------
        # USER ID
        # --------------------------------------------------------

        elif ButtonUtils.is_number(data):
            kwargs["user_id"] = int(data)

        # --------------------------------------------------------
        # COPY
        # --------------------------------------------------------

        elif ButtonUtils.is_copy(data):
            kwargs["copy_text"] = data.replace(
                "copy:",
                "",
                1,
            )

        # --------------------------------------------------------
        # ALERT
        # --------------------------------------------------------

        elif ButtonUtils.is_alert(data):
            alert_text = data.replace(
                "alert:",
                "",
                1,
            )

            uniq = str(uuid4().int)[:8]

            await dB.set_var(
                int(uniq),
                int(uniq),
                alert_text,
            )

            kwargs["callback_data"] = (
                f"alertcb_{int(uniq)}"
            )

        # --------------------------------------------------------
        # CALLBACK
        # --------------------------------------------------------

        else:
            kwargs["callback_data"] = (
                f"{data}_{with_suffix}"
                if with_suffix
                else data
            )

        # --------------------------------------------------------
        # STYLE
        #
        # Style only applies to callback buttons.
        # --------------------------------------------------------

        button_style = ButtonUtils.get_style(
            style
        )

        if (
            button_style is not None
            and "callback_data" in kwargs
        ):
            kwargs["style"] = button_style

        return InlineKeyboardButton(
            **kwargs
        )

    # ============================================================
    # CREATE INLINE KEYBOARD
    # ============================================================

    @staticmethod
    async def create_inline_keyboard(
        buttons: List[List],
        suffix: str = "",
    ) -> InlineKeyboardMarkup:
        """
        Create InlineKeyboardMarkup.

        Input:

        [
            [
                ["Delete", "delete", "danger"],
                ["Confirm", "confirm", "success"]
            ]
        ]
        """

        keyboard = []

        for row in buttons:
            keyboard_row = []

            for button in row:
                if len(button) < 2:
                    continue

                text = button[0]
                data = button[1]

                style = (
                    button[2]
                    if len(button) >= 3
                    else None
                )

                keyboard_row.append(
                    await ButtonUtils.create_button(
                        text=text,
                        data=data,
                        with_suffix=suffix,
                        style=style,
                    )
                )

            if keyboard_row:
                keyboard.append(
                    keyboard_row
                )

        return InlineKeyboardMarkup(
            keyboard
        )

    # ============================================================
    # START MENU
    # ============================================================

    @staticmethod
    def start_menu(
        user_id: int,
    ) -> kb:
        """Generate start menu keyboard."""

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

    # ============================================================
    # USERBOT LIST
    # ============================================================

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
                ButtonUtils.styled_button(
                    "❮",
                    f"prev_ub {count}",
                    "primary",
                )
            )

        page_number = (
            count // 10
        ) * 10

        nav_buttons.append(
            ButtonUtils.styled_button(
                "Kembali",
                f"bcpg_acc {page_number}",
                "primary",
            )
        )

        if count < total_count - 1:
            nav_buttons.append(
                ButtonUtils.styled_button(
                    "❯",
                    f"next_ub {count}",
                    "primary",
                )
            )

        buttons.append(
            nav_buttons
        )

        action_buttons = [
            [
                ButtonUtils.styled_button(
                    "Get OTP",
                    f"get_otp {count}",
                    "success",
                ),
            ],
            [
                ButtonUtils.styled_button(
                    "Hapus User",
                    f"del_ubot {user_id}",
                    "danger",
                ),
                ButtonUtils.styled_button(
                    "Hapus Akun",
                    f"ub_deak {count}",
                    "danger",
                ),
            ],
        ]

        buttons.extend(
            action_buttons
        )

        return InlineKeyboardMarkup(
            buttons
        )

    # ============================================================
    # ACCOUNT LIST
    # ============================================================

    @staticmethod
    def account_list(
        start_index=0,
    ):
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

            button = ButtonUtils.styled_button(
                f"{i + 1}",
                f"tools_acc {user_id}-{i}",
                "primary",
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
                ButtonUtils.styled_button(
                    "◀️ Prev page",
                    f"acc_page {start_index - 10}",
                    "primary",
                )
            )

        if end_index < total_users:
            nav_buttons.append(
                ButtonUtils.styled_button(
                    "Next page ▶️",
                    f"acc_page {end_index}",
                    "primary",
                )
            )

        if nav_buttons:
            buttons.append(
                nav_buttons
            )

        buttons.append(
            [
                ButtonUtils.styled_button(
                    "Tutup",
                    "buttonclose",
                    "danger",
                )
            ]
        )

        return InlineKeyboardMarkup(
            buttons
        )

    # ============================================================
    # DEACTIVATE
    # ============================================================

    @staticmethod
    def deak(
        user_id,
        count,
    ):
        return InlineKeyboardMarkup(
            [
                [
                    ButtonUtils.styled_button(
                        "⬅️",
                        f"prev_ub {int(count)}",
                        "primary",
                    ),
                    ButtonUtils.styled_button(
                        "Approve",
                        f"deak_akun {int(count)}",
                        "success",
                    ),
                ]
            ]
        )

    # ============================================================
    # INLINE QUERY
    # ============================================================

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

    # ============================================================
    # SEND INLINE BOT RESULT
    # ============================================================

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
            query_results = (
                await ButtonUtils.generate_inline_query(
                    message,
                    chat_id,
                    bot_username,
                    query,
                )
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

    # ============================================================
    # BUILD BUTTONS
    # ============================================================

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
                ButtonUtils.styled_button(
                    str(idx + 1),
                    f"{callback}{idx}_{uniq}",
                    "primary",
                )
            )

            if len(row) == 5:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        buttons.append(
            [
                ButtonUtils.styled_button(
                    "❌ Close",
                    f"close {closed} {uniq}",
                    "danger",
                )
            ]
        )

        return InlineKeyboardMarkup(
            buttons
        )

    # ============================================================
    # PLUS MINUS
    # ============================================================

    @staticmethod
    def plus_minus(
        bulan,
        harga,
        plan,
    ):
        return InlineKeyboardMarkup(
            [
                [
                    ButtonUtils.styled_button(
                        "⁻1 bulan",
                        f"kurang {bulan} {harga} {plan}",
                        "danger",
                    ),
                    ButtonUtils.styled_button(
                        "⁺1 bulan",
                        f"tambah {bulan} {harga} {plan}",
                        "success",
                    ),
                ],
                [
                    ButtonUtils.styled_button(
                        "Konfirmasi",
                        f"confirm {bulan} {harga} {plan}",
                        "success",
                    )
                ],
                [
                    ButtonUtils.styled_button(
                        "Batal",
                        "buttonclose",
                        "danger",
                    )
                ],
            ]
        )

    # ============================================================
    # CHOOSE PLAN
    # ============================================================

    @staticmethod
    def chose_plan():
        return InlineKeyboardMarkup(
            [
                [
                    ButtonUtils.styled_button(
                        "🧩 Plan Basic",
                        "planusers basic",
                        "primary",
                    ),
                    ButtonUtils.styled_button(
                        "💎 Plan Pro",
                        "planusers is_pro",
                        "success",
                    ),
                ],
                [
                    ButtonUtils.styled_button(
                        "⚡ Plan Lite",
                        "planusers lite",
                        "primary",
                    )
                ],
                [
                    ButtonUtils.styled_button(
                        "Batal",
                        "buttonclose",
                        "danger",
                    )
                ],
            ]
        )

    # ============================================================
    # FONT KEYBOARD
    # ============================================================

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
                    ButtonUtils.styled_button(
                        key,
                        f"get_font {get_id} {value}",
                        "primary",
                    )
                )

        rows = [
            keyboard[i : i + 2]
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
                ButtonUtils.styled_button(
                    "⬅️",
                    f"prev_font {get_id} {current_batch}",
                    "primary",
                ),
                ButtonUtils.styled_button(
                    "❌",
                    f"close inline_font {get_id}",
                    "danger",
                ),
                ButtonUtils.styled_button(
                    "➡️",
                    f"next_font {get_id} {current_batch}",
                    "primary",
                ),
            ]
        )

        return rows
