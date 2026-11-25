"""Markdown (as written by the model) -> Telegram HTML, plus safe message splitting."""
from __future__ import annotations

import html
import re

TG_LIMIT = 4096
CHUNK = 3300  # raw-markdown size per message; leaves room for HTML escaping/tags

_FENCE = re.compile(r"```([\w+#.\-]*)[^\n]*\n(.*?)(?:```|\Z)", re.S)
_INLINE = re.compile(r"`([^`\n]+)`")
_TABLE_BLOCK = re.compile(r"(?:^\|.*\|[ \t]*\n?)+", re.M)


def md_to_html(text: str) -> str:
    stash: list[str] = []

    def keep(s: str) -> str:
        stash.append(s)
        return f"\x00{len(stash) - 1}\x00"

    def fence(m: re.Match) -> str:
        lang, code = m.group(1), m.group(2).rstrip("\n")
        cls = f' class="language-{html.escape(lang)}"' if lang else ""
        return keep(f"<pre><code{cls}>{html.escape(code)}</code></pre>")

    text = _FENCE.sub(fence, text)
    text = _TABLE_BLOCK.sub(lambda m: keep(f"<pre>{html.escape(m.group(0).rstrip())}</pre>\n"), text)
    text = _INLINE.sub(lambda m: keep(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = html.escape(text, quote=False)

    text = re.sub(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", r"<b>\1</b>", text, flags=re.M)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    text = re.sub(r"(?<![\w_])_(?!\s)([^_\n]+?)(?<!\s)_(?![\w_])", r"<i>\1</i>", text)
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    text = re.sub(
        r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)",
        lambda m: f'<a href="{m.group(2).replace(chr(34), "%22")}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"^(\s*)[-*+]\s+", r"\1• ", text, flags=re.M)
    text = re.sub(r"^-{3,}\s*$", "──────", text, flags=re.M)
    # blockquotes ("> text" was escaped to "&gt; text")
    text = re.sub(
        r"((?:^&gt;\s?.*(?:\n|$))+)",
        lambda m: "<blockquote>"
        + re.sub(r"^&gt;\s?", "", m.group(1).rstrip("\n"), flags=re.M)
        + "</blockquote>\n",
        text,
        flags=re.M,
    )
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text).strip()


def split_markdown(text: str, limit: int = CHUNK) -> list[str]:
    """Split on line boundaries without leaving a code fence open across chunks."""
    text = text.strip()
    if len(text) <= limit:
        return [text] if text else []
    chunks: list[str] = []
    cur: list[str] = []
    size = 0
    fence_open: str | None = None

    def flush() -> None:
        nonlocal cur, size
        body = "\n".join(cur).strip("\n")
        if fence_open is not None:
            body += "\n```"
        if body.strip():
            chunks.append(body)
        cur = [fence_open] if fence_open is not None else []
        size = len(fence_open) if fence_open is not None else 0

    for line in text.split("\n"):
        while len(line) > limit:  # absurdly long single line
            head, line = line[:limit], line[limit:]
            if size + len(head) + 1 > limit:
                flush()
            cur.append(head)
            size += len(head) + 1
            flush()
        if size + len(line) + 1 > limit and cur:
            flush()
        cur.append(line)
        size += len(line) + 1
        if line.lstrip().startswith("```"):
            fence_open = None if fence_open is not None else line.strip()
    body = "\n".join(cur).strip("\n")
    if body.strip():
        chunks.append(body)
    return chunks


def code_blocks(text: str) -> list[tuple[str, str]]:
    return [(m.group(1).lower(), m.group(2)) for m in _FENCE.finditer(text)]
