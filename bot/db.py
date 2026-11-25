from __future__ import annotations

import contextlib
import os
from typing import Any

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER PRIMARY KEY,
    lang       TEXT,
    mode       TEXT NOT NULL DEFAULT 'chat',
    style      TEXT NOT NULL DEFAULT 'normal',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    role       TEXT NOT NULL,
    content    TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, id);
"""

_USER_FIELDS = {"lang", "mode", "style"}


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True, mode=0o700)
        self.conn = await aiosqlite.connect(self.path)
        with contextlib.suppress(OSError):
            os.chmod(self.path, 0o600)  # chat history is private
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    # ---- users -----------------------------------------------------------
    async def get_user(self, uid: int) -> dict[str, Any] | None:
        async with self.conn.execute("SELECT * FROM users WHERE user_id=?", (uid,)) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None

    async def ensure_user(self, uid: int) -> dict[str, Any]:
        await self.conn.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (uid,))
        await self.conn.commit()
        return await self.get_user(uid)  # type: ignore[return-value]

    async def update_user(self, uid: int, **fields: str) -> None:
        fields = {k: v for k, v in fields.items() if k in _USER_FIELDS}
        if not fields:
            return
        await self.ensure_user(uid)
        sets = ", ".join(f"{k}=?" for k in fields)
        await self.conn.execute(f"UPDATE users SET {sets} WHERE user_id=?", (*fields.values(), uid))
        await self.conn.commit()

    # ---- history ---------------------------------------------------------
    async def add_message(self, uid: int, role: str, content: str) -> None:
        await self.conn.execute(
            "INSERT INTO messages(user_id, role, content) VALUES (?,?,?)", (uid, role, content)
        )
        await self.conn.commit()

    async def history(self, uid: int, limit: int) -> list[dict[str, str]]:
        async with self.conn.execute(
            "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (uid, limit),
        ) as cur:
            rows = [dict(r) for r in await cur.fetchall()]
        rows.reverse()
        while rows and rows[0]["role"] != "user":  # API wants the first turn to be the user's
            rows.pop(0)
        return rows

    async def pop_last(self, uid: int, role: str) -> None:
        await self.conn.execute(
            "DELETE FROM messages WHERE id = (SELECT MAX(id) FROM messages "
            "WHERE user_id=? AND role=?)",
            (uid, role),
        )
        await self.conn.commit()

    async def last_assistant(self, uid: int) -> str | None:
        async with self.conn.execute(
            "SELECT content FROM messages WHERE user_id=? AND role='assistant' "
            "ORDER BY id DESC LIMIT 1",
            (uid,),
        ) as cur:
            row = await cur.fetchone()
        return row["content"] if row else None

    async def trim(self, uid: int, keep: int) -> None:
        await self.conn.execute(
            "DELETE FROM messages WHERE user_id=? AND id NOT IN "
            "(SELECT id FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?)",
            (uid, uid, keep),
        )
        await self.conn.commit()

    async def clear_history(self, uid: int) -> None:
        await self.conn.execute("DELETE FROM messages WHERE user_id=?", (uid,))
        await self.conn.commit()
