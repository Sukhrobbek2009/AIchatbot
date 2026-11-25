from __future__ import annotations

import asyncio
import contextlib
import io
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, FSInputFile, Message
from google.genai import errors as genai_errors

from . import keyboards as kb
from .ai import AI
from .animations import LiveReply
from .config import Config
from .db import Database
from .files import TEXT_EXTS, answer_to_file, parse_files
from .i18n import DEFAULT_LANG, LANGS, t
from .prompts import MODES, build_system

log = logging.getLogger(__name__)

GUIDE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt_guide.html")
MAX_FILE_MB = 10
MAX_DOC_CHARS = 150_000


@dataclass
class App:
    cfg: Config
    db: Database
    ai: AI
    sem: asyncio.Semaphore
    locks: dict[int, asyncio.Lock] = field(default_factory=dict)
    active: dict[int, asyncio.Task] = field(default_factory=dict)

    hits: dict[int, deque] = field(default_factory=dict)

    def lock(self, uid: int) -> asyncio.Lock:
        return self.locks.setdefault(uid, asyncio.Lock())

    def rate_limited(self, uid: int) -> bool:
        """Sliding 60-second window per user. Protects the API quota/bill from spam."""
        limit = self.cfg.rate_limit_per_min
        if limit <= 0:
            return False
        now = time.monotonic()
        q = self.hits.setdefault(uid, deque())
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= limit:
            return True
        q.append(now)
        return False


def error_key(e: Exception) -> str:
    if isinstance(e, genai_errors.ClientError):
        if e.code == 429:
            return "err_rate"
        if e.code in (400, 401, 403, 404):
            # bad/expired key, API not enabled, unknown model name, region restriction...
            log.error("Gemini rejected the request (%s): %s", e.code, e.message)
            return "err_config"
        log.warning("Gemini client error %s: %s", e.code, e.message)
        return "err_generic"
    if isinstance(e, genai_errors.ServerError):
        log.warning("Gemini server error %s: %s", e.code, e.message)
        return "err_overloaded"
    if isinstance(e, (ConnectionError, TimeoutError)):
        log.warning("Gemini connection problem: %s", e)
        return "err_overloaded"
    log.error("Unhandled generation error", exc_info=e)
    return "err_generic"


def build_router(app: App) -> Router:
    r = Router()
    db, cfg = app.db, app.cfg

    @r.message.outer_middleware()
    @r.callback_query.outer_middleware()
    async def access_control(handler, event, data):
        """Single gate: with ALLOWED_USERS set, nobody else reaches any handler."""
        user = event.from_user
        if user is None or (cfg.allowed_users and user.id not in cfg.allowed_users):
            if isinstance(event, Message):
                await event.answer(t(DEFAULT_LANG, "not_allowed"))
            else:
                await event.answer(t(DEFAULT_LANG, "not_allowed"), show_alert=True)
            return None
        return await handler(event, data)

    async def lang_of(uid: int) -> str:
        u = await db.get_user(uid)
        return (u or {}).get("lang") or DEFAULT_LANG

    def allowed(uid: int) -> bool:
        return not cfg.allowed_users or uid in cfg.allowed_users

    async def menu_text(uid: int):
        u = await db.ensure_user(uid)
        lang = u["lang"] or DEFAULT_LANG
        return (
            t(lang, "menu", mode=t(lang, f"mode_{u['mode']}")),
            kb.modes_kb(lang, u["mode"]),
        )

    # ------------------------------------------------------------------ commands
    @r.message(CommandStart())
    async def start(m: Message) -> None:
        if not allowed(m.from_user.id):
            return await m.answer(t(DEFAULT_LANG, "not_allowed"))
        u = await db.ensure_user(m.from_user.id)
        if not u["lang"]:
            return await m.answer(t(DEFAULT_LANG, "choose_lang"), reply_markup=kb.lang_kb())
        await send_welcome(m.bot, m.chat.id, m.from_user, u["lang"])

    async def send_welcome(bot: Bot, chat_id: int, user, lang: str) -> None:
        text, markup = await menu_text(user.id)
        await bot.send_message(chat_id, t(lang, "welcome", name=user.first_name or ""))
        await bot.send_message(chat_id, text, reply_markup=markup)

    @r.message(Command("menu", "mode"))
    async def menu(m: Message) -> None:
        if not allowed(m.from_user.id):
            return
        text, markup = await menu_text(m.from_user.id)
        await m.answer(text, reply_markup=markup)

    @r.message(Command("new"))
    async def new_chat(m: Message) -> None:
        if not allowed(m.from_user.id):
            return
        await db.clear_history(m.from_user.id)
        await m.answer(t(await lang_of(m.from_user.id), "new_done"))

    @r.message(Command("lang"))
    async def lang_cmd(m: Message) -> None:
        if not allowed(m.from_user.id):
            return
        await m.answer(t(await lang_of(m.from_user.id), "choose_lang"), reply_markup=kb.lang_kb())

    @r.message(Command("help"))
    async def help_cmd(m: Message) -> None:
        if not allowed(m.from_user.id):
            return
        await m.answer(t(await lang_of(m.from_user.id), "help"))

    @r.message(Command("settings"))
    async def settings_cmd(m: Message) -> None:
        if not allowed(m.from_user.id):
            return
        await send_settings(m, m.from_user.id)

    @r.message(Command("guide"))
    async def guide_cmd(m: Message) -> None:
        if not allowed(m.from_user.id):
            return
        await send_guide(m.chat.id, m.bot, await lang_of(m.from_user.id))

    async def send_guide(chat_id: int, bot: Bot, lang: str) -> None:
        await bot.send_document(
            chat_id, FSInputFile(GUIDE_PATH, filename="prompt_guide.html"),
            caption=t(lang, "guide_caption"),
        )

    async def send_settings(m: Message, uid: int, edit: bool = False) -> None:
        u = await db.ensure_user(uid)
        lang = u["lang"] or DEFAULT_LANG
        text = t(lang, "settings", style=t(lang, f"style_label_{u['style']}"), lang=LANGS[lang])
        markup = kb.settings_kb(lang, u["style"])
        if edit:
            with contextlib.suppress(TelegramBadRequest):
                await m.edit_text(text, reply_markup=markup)
            return
        await m.answer(text, reply_markup=markup)

    # ------------------------------------------------------------------ callbacks
    @r.callback_query(F.data.startswith("lang:"))
    async def pick_lang(c: CallbackQuery) -> None:
        if not allowed(c.from_user.id):
            return await c.answer()
        code = c.data.split(":")[1]
        if code not in LANGS:
            return await c.answer()
        first_time = not (await db.ensure_user(c.from_user.id))["lang"]
        await db.update_user(c.from_user.id, lang=code)
        await c.answer(t(code, "lang_set"))
        chat_id = c.message.chat.id
        with contextlib.suppress(TelegramBadRequest):
            await c.message.delete()
        if first_time:
            await send_welcome(c.bot, chat_id, c.from_user, code)
        else:
            text, markup = await menu_text(c.from_user.id)
            await c.bot.send_message(chat_id, text, reply_markup=markup)

    @r.callback_query(F.data.startswith("mode:"))
    async def pick_mode(c: CallbackQuery) -> None:
        mode = c.data.split(":")[1]
        if mode not in MODES:
            return await c.answer()
        await db.update_user(c.from_user.id, mode=mode)
        lang = await lang_of(c.from_user.id)
        await c.answer(t(lang, f"mode_{mode}"))
        text = t(lang, "mode_set", mode=t(lang, f"mode_{mode}"), hint=t(lang, f"hint_{mode}"))
        with contextlib.suppress(TelegramBadRequest):
            await c.message.edit_text(text, reply_markup=kb.modes_kb(lang, mode))

    @r.callback_query(F.data.startswith("style:"))
    async def pick_style(c: CallbackQuery) -> None:
        style = c.data.split(":")[1]
        if style in ("short", "normal", "detailed"):
            await db.update_user(c.from_user.id, style=style)
        await c.answer("✓")
        await send_settings(c.message, c.from_user.id, edit=True)

    @r.callback_query(F.data.startswith("act:"))
    async def actions(c: CallbackQuery) -> None:
        act, uid = c.data.split(":")[1], c.from_user.id
        lang = await lang_of(uid)
        await c.answer()
        chat_id = c.message.chat.id
        if act == "new":
            await db.clear_history(uid)
            await c.bot.send_message(chat_id, t(lang, "new_done"))
        elif act == "lang":
            await c.bot.send_message(chat_id, t(lang, "choose_lang"), reply_markup=kb.lang_kb())
        elif act == "guide":
            await send_guide(chat_id, c.bot, lang)
        elif act == "help":
            await c.bot.send_message(chat_id, t(lang, "help"))
        elif act == "settings":
            await send_settings(c.message, uid)
        elif act == "menu":
            text, markup = await menu_text(uid)
            await c.bot.send_message(chat_id, text, reply_markup=markup)

    @r.callback_query(F.data == "stop")
    async def stop(c: CallbackQuery) -> None:
        task = app.active.get(c.from_user.id)
        await c.answer(t(await lang_of(c.from_user.id), "stopped"))
        if task and not task.done():
            task.cancel()

    @r.callback_query(F.data.startswith("re:"))
    async def regenerate(c: CallbackQuery) -> None:
        uid, what = c.from_user.id, c.data.split(":")[1]
        lang = await lang_of(uid)
        chat_id = c.message.chat.id
        if what != "file" and app.lock(uid).locked():
            return await c.answer(t(lang, "busy"), show_alert=True)
        await c.answer()
        if what == "file":
            last = await db.last_assistant(uid)
            if not last:
                return await c.bot.send_message(chat_id, t(lang, "file_none"))
            f = answer_to_file(last)
            await c.bot.send_document(
                chat_id, BufferedInputFile(f.data, filename=f.name), caption=t(lang, "file_ready")
            )
            return
        with contextlib.suppress(TelegramBadRequest):
            await c.message.edit_reply_markup(reply_markup=None)
        if what == "regen":
            await db.pop_last(uid, "assistant")
            hist = await db.history(uid, 1)
            if not hist or hist[-1]["role"] != "user":
                return
            await run_task(c.bot, chat_id, uid, None)
        elif what in ("short", "long"):
            follow = {
                "short": "Please make your previous answer shorter and more concise.",
                "long": "Please expand your previous answer with more detail and examples.",
            }[what]
            await run_task(c.bot, chat_id, uid, follow)

    # ------------------------------------------------------------------ input handling
    async def guard(m: Message) -> bool:
        if allowed(m.from_user.id):
            return True
        await m.answer(t(DEFAULT_LANG, "not_allowed"))
        return False

    async def ensure_lang(m: Message) -> str | None:
        u = await db.ensure_user(m.from_user.id)
        if not u["lang"]:
            await m.answer(t(DEFAULT_LANG, "choose_lang"), reply_markup=kb.lang_kb())
            return None
        return u["lang"]

    async def download(m: Message, file_id: str, size: int | None, lang: str) -> bytes | None:
        if size and size > MAX_FILE_MB * 1024 * 1024:
            await m.answer(t(lang, "too_big", mb=MAX_FILE_MB))
            return None
        buf = io.BytesIO()
        await m.bot.download(file_id, destination=buf)
        data = buf.getvalue()
        if len(data) > MAX_FILE_MB * 1024 * 1024:  # file_size from Telegram may be missing
            await m.answer(t(lang, "too_big", mb=MAX_FILE_MB))
            return None
        return data

    @r.message(F.photo)
    async def on_photo(m: Message) -> None:
        if not await guard(m) or not (lang := await ensure_lang(m)):
            return
        if app.lock(m.from_user.id).locked():
            return await m.answer(t(lang, "busy"))
        data = await download(m, m.photo[-1].file_id, m.photo[-1].file_size, lang)
        if data is None:
            return
        caption = m.caption or t(lang, "img_default")
        blocks = [
            {"type": "bytes", "mime": "image/jpeg", "data": data},
            {"type": "text", "text": caption},
        ]
        await run_task(m.bot, m.chat.id, m.from_user.id, caption, blocks,
                       history_text=f"[image] {caption}")

    @r.message(F.document)
    async def on_document(m: Message) -> None:
        if not await guard(m) or not (lang := await ensure_lang(m)):
            return
        doc = m.document
        ext = os.path.splitext((doc.file_name or "").lower())[1]
        is_pdf = doc.mime_type == "application/pdf" or ext == ".pdf"
        is_text = (doc.mime_type or "").startswith("text/") or ext in TEXT_EXTS
        if not (is_pdf or is_text):
            return await m.answer(t(lang, "unsupported"))
        if app.lock(m.from_user.id).locked():
            return await m.answer(t(lang, "busy"))
        data = await download(m, doc.file_id, doc.file_size, lang)
        if data is None:
            return
        caption = m.caption or t(lang, "doc_default")
        if is_pdf:
            blocks = [
                {"type": "bytes", "mime": "application/pdf", "data": data},
                {"type": "text", "text": caption},
            ]
        else:
            body = data.decode("utf-8", errors="replace")[:MAX_DOC_CHARS]
            blocks = [{"type": "text", "text": f"File `{doc.file_name}`:\n\n{body}\n\n---\n{caption}"}]
        await run_task(m.bot, m.chat.id, m.from_user.id, caption, blocks,
                       history_text=f"[file: {doc.file_name}] {caption}")

    @r.message(F.text & ~F.text.startswith("/"))
    async def on_text(m: Message) -> None:
        if not await guard(m) or not (lang := await ensure_lang(m)):
            return
        if app.lock(m.from_user.id).locked():
            return await m.answer(t(lang, "busy"))
        await run_task(m.bot, m.chat.id, m.from_user.id, m.text)

    @r.message()
    async def on_other(m: Message) -> None:
        if not await guard(m) or not (lang := await ensure_lang(m)):
            return
        await m.answer(t(lang, "unsupported"))

    # ------------------------------------------------------------------ generation pipeline
    async def run_task(bot: Bot, chat_id: int, uid: int, text: str | None,
                       blocks: list | None = None, history_text: str | None = None) -> None:
        """Run the pipeline as its own task so the ⏹ button can cancel it."""
        if app.rate_limited(uid):
            await bot.send_message(chat_id, t(await lang_of(uid), "err_ratelimit"))
            return
        task = asyncio.create_task(pipeline(bot, chat_id, uid, text, blocks, history_text))
        app.active[uid] = task
        try:
            await task
        finally:
            app.active.pop(uid, None)

    async def pipeline(bot: Bot, chat_id: int, uid: int, text: str | None,
                       blocks: list | None, history_text: str | None) -> None:
        async with app.lock(uid), app.sem:
            u = await db.ensure_user(uid)
            lang, mode, style = u["lang"] or DEFAULT_LANG, u["mode"], u["style"]
            if text is not None:
                await db.add_message(uid, "user", history_text or text)
            history = await db.history(uid, cfg.max_history)
            messages = [{"role": h["role"], "content": h["content"]} for h in history]
            if blocks and messages:
                messages[-1]["content"] = blocks  # rich content only for the current turn

            mode_cfg = MODES.get(mode, MODES["chat"])
            live = LiveReply(bot, chat_id, lang, kb.stop_kb(lang), hide_stream=(mode == "files"))
            await live.start()
            try:
                result = await app.ai.generate(
                    system=build_system(mode, style, lang),
                    messages=messages,
                    max_tokens=mode_cfg["max_tokens"],
                    on_text=live.push,
                )
            except asyncio.CancelledError:
                partial = live.buffer.strip()
                if partial and mode != "files":
                    await live.finish(partial, kb.answer_kb(lang), note=t(lang, "stopped_note"))
                    await db.add_message(uid, "assistant", partial)
                else:
                    await live.fail(t(lang, "stopped"))
                    await db.pop_last(uid, "user")
                return
            except Exception as e:
                await live.fail(t(lang, error_key(e)))
                await db.pop_last(uid, "user")
                return

            if result.refused or not result.text.strip():
                await live.fail(t(lang, "refused"))
                await db.pop_last(uid, "user")
                return

            await deliver(bot, chat_id, live, lang, mode, result)
            await db.add_message(uid, "assistant", result.text)
            await db.trim(uid, cfg.max_history * 2)

    async def deliver(bot: Bot, chat_id: int, live: LiveReply, lang: str, mode: str, result) -> None:
        note = t(lang, "truncated") if result.truncated else ""
        if mode == "files":
            message, files = parse_files(result.text)
            if files:
                await live.finish(message or t(lang, "file_ready"), note=note)
                for f in files:
                    await bot.send_document(chat_id, BufferedInputFile(f.data, filename=f.name))
                await bot.send_message(chat_id, "👇", reply_markup=kb.answer_kb(lang, with_file=False))
                return
        await live.finish(result.text, kb.answer_kb(lang), note=note)

    return r
