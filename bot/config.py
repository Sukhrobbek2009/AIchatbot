from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    # repr=False keeps secrets out of logs/tracebacks if the config is ever printed
    bot_token: str = field(repr=False)
    gemini_api_key: str = field(repr=False)
    model: str
    db_path: str
    max_history: int
    max_concurrent: int
    rate_limit_per_min: int
    allowed_users: frozenset[int]


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not token or token.startswith("123456:ABC"):
        raise SystemExit("BOT_TOKEN is missing. Put your @BotFather token in .env.")
    if not key or key == "your-gemini-api-key":
        raise SystemExit("GEMINI_API_KEY is missing. Put your key (https://aistudio.google.com/apikey) in .env.")
    allowed = frozenset(
        int(x) for x in os.getenv("ALLOWED_USERS", "").replace(" ", "").split(",") if x.isdigit()
    )
    return Config(
        bot_token=token,
        gemini_api_key=key,
        model=os.getenv("MODEL", "gemini-2.5-flash").strip(),
        db_path=os.getenv("DB_PATH", "data/bot.db"),
        max_history=int(os.getenv("MAX_HISTORY", "20")),
        max_concurrent=int(os.getenv("MAX_CONCURRENT", "20")),
        rate_limit_per_min=int(os.getenv("RATE_LIMIT_PER_MIN", "12")),
        allowed_users=allowed,
    )
