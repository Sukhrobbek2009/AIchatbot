"""Live 'typing' reply: animated spinner while thinking, then a streaming message with a cursor."""
from __future__ import annotations

import asyncio
import contextlib
import logging

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, Message

from .formatting import TG_LIMIT, md_to_html, split_markdown
from .i18n import t

log = logging.getLogger(__name__)

SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
TICK = 0.9  # seconds between edits - stays under Telegram's edit rate limits


class LiveReply:
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        lang: str,
        stop_markup: InlineKeyboardMarkup | None = None,
        hide_stream: bool = False,
    ) -> None:
        self.bot, self.chat_id, self.lang = bot, chat_id, lang
        self.stop_markup = stop_markup
        self.hide_stream = hide_stream  # show progress instead of raw text (file generation)
        self.buffer = ""
        self.msg: Message | None = None
        self._last = ""
        self._frame = 0
        self._tasks: list[asyncio.Task] = []

    # ---- lifecycle -------------------------------------------------------
    async def start(self) -> None:
        self.msg = await self.bot.send_message(
            self.chat_id, self._render(), reply_markup=self.stop_markup
        )
        self._last = self._render()
        self._tasks = [asyncio.create_task(self._animate()), asyncio.create_task(self._typing())]

    async def push(self, delta: str) -> None:
        self.buffer += delta

    async def _stop_tasks(self) -> None:
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task
        self._tasks = []

    # ---- animation -------------------------------------------------------
    def _render(self) -> str:
        frame = SPINNER[self._frame % len(SPINNER)]
        if not self.buffer:
            phrases = t(self.lang, "thinking")
            phrase = phrases[min(self._frame // 5, len(phrases) - 1)]
            dots = "." * (self._frame % 4)
            return f"{frame} {phrase}{dots}"
        if self.hide_stream:
            return f"{frame} {t(self.lang, 'writing_file')} · {len(self.buffer):,} chars"
        shown = self.buffer
        if len(shown) > TG_LIMIT - 20:
            shown = "…" + shown[-(TG_LIMIT - 40):]
        return f"{shown} ▍"

    async def _animate(self) -> None:
        while True:
            await asyncio.sleep(TICK)
            self._frame += 1
            text = self._render()
            if text == self._last:
                continue
            try:
                await self.bot.edit_message_text(
                    text, self.chat_id, self.msg.message_id, reply_markup=self.stop_markup
                )
                self._last = text
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except TelegramBadRequest:
                pass
            except Exception:  # network hiccup - keep animating
                log.debug("animation edit failed", exc_info=True)

    async def _typing(self) -> None:
        while True:
            with contextlib.suppress(Exception):
                await self.bot.send_chat_action(self.chat_id, ChatAction.TYPING)
            await asyncio.sleep(4.5)

    # ---- finishing -------------------------------------------------------
    async def finish(
        self, text: str, markup: InlineKeyboardMarkup | None = None, note: str = ""
    ) -> None:
        await self._stop_tasks()
        chunks = split_markdown(text) or ["…"]
        for i, chunk in enumerate(chunks):
            last = i == len(chunks) - 1
            body = md_to_html(chunk)
            if last and note:
                body += f"\n\n{note}"
            kb = markup if last else None
            if i == 0:
                await self._edit_or_send(body, chunk, kb, edit=True)
            else:
                await self._edit_or_send(body, chunk, kb, edit=False)

    async def _edit_or_send(self, html_body: str, plain: str, kb, edit: bool) -> None:
        for attempt in range(3):
            try:
                if len(html_body) > TG_LIMIT:
                    raise TelegramBadRequest(method=None, message="too long")  # type: ignore[arg-type]
                if edit:
                    await self.bot.edit_message_text(
                        html_body, self.chat_id, self.msg.message_id,
                        parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True,
                    )
                else:
                    await self.bot.send_message(
                        self.chat_id, html_body, parse_mode="HTML", reply_markup=kb,
                        disable_web_page_preview=True,
                    )
                return
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after + 0.5)
            except TelegramBadRequest as e:
                if "not modified" in str(e):
                    return
                # HTML rejected -> plain text fallback
                plain_text = plain[: TG_LIMIT - 1]
                if edit:
                    with contextlib.suppress(TelegramBadRequest):
                        await self.bot.edit_message_text(
                            plain_text, self.chat_id, self.msg.message_id, reply_markup=kb
                        )
                else:
                    await self.bot.send_message(self.chat_id, plain_text, reply_markup=kb)
                return
        log.warning("gave up delivering a message chunk after retries")

    async def fail(self, text: str) -> None:
        await self._stop_tasks()
        try:
            await self.bot.edit_message_text(
                text, self.chat_id, self.msg.message_id, parse_mode="HTML"
            )
        except TelegramBadRequest:
            with contextlib.suppress(Exception):
                await self.bot.send_message(self.chat_id, text, parse_mode="HTML")

    async def delete(self) -> None:
        await self._stop_tasks()
        with contextlib.suppress(Exception):
            await self.bot.delete_message(self.chat_id, self.msg.message_id)
