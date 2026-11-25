from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from .ai import AI
from .config import load_config
from .db import Database
from .handlers import App, build_router
from .i18n import LANGS, t

COMMANDS = ["start", "menu", "new", "mode", "lang", "settings", "guide", "help"]


async def setup_commands(bot: Bot) -> None:
    for code in LANGS:
        cmds = [BotCommand(command=c, description=t(code, f"cmd_{c}")[:256]) for c in COMMANDS]
        await bot.set_my_commands(cmds, language_code=code)
    await bot.set_my_commands(
        [BotCommand(command=c, description=t("en", f"cmd_{c}")) for c in COMMANDS]
    )


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpcore", "aiohttp", "google_genai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)  # never log request URLs/headers
    cfg = load_config()
    db = Database(cfg.db_path)
    await db.connect()
    bot = Bot(cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = App(cfg=cfg, db=db, ai=AI(cfg), sem=asyncio.Semaphore(cfg.max_concurrent))
    dp = Dispatcher()
    dp.include_router(build_router(app))
    try:
        await setup_commands(bot)
        me = await bot.get_me()
        logging.info("Bot @%s started (model: %s)", me.username, cfg.model)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


def main() -> None:
    try:
        asyncio.run(run())
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
