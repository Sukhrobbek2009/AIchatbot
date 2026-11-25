# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
source .venv/bin/activate          # venv already exists; deps in requirements.txt
# .env (git-ignored, chmod 600) needs BOT_TOKEN and GEMINI_API_KEY; template in .env.example
python run.py                      # start the bot (long polling, no server needed)
```

There is no test suite, linter, or build step. Offline checks used so far were ad-hoc scripts: a fake `Bot` object to exercise `LiveReply`, and direct calls to `md_to_html` / `split_markdown` / `parse_files`. The real Telegram and Gemini APIs have not been exercised without credentials.

## Architecture

Python 3.14 + aiogram 3 (long polling) + `google-genai` SDK (Gemini) + SQLite (aiosqlite). Entry: `run.py` -> `bot/main.py`, which wires `Config`, `Database`, `AI` into an `App` dataclass and registers the single router from `bot/handlers.py:build_router(app)`.

**Request flow (spans handlers.py, ai.py, animations.py, formatting.py, files.py):**
1. A text/photo/document handler builds the input and calls `run_task`, which runs `pipeline` as its own `asyncio.Task` stored in `app.active[uid]` so the inline ⏹ button can `cancel()` it. `pipeline` catches `CancelledError` itself and saves/finishes the partial answer; don't re-raise it there.
2. `pipeline` holds a per-user lock (`app.lock(uid)`, handlers reject with "busy" if locked) plus a global semaphore, saves the user turn to SQLite, loads the last `MAX_HISTORY` messages, and swaps the final message's content for rich blocks (image/PDF/file text) for the current turn only. History stores text only (e.g. `[image] caption`).
3. `AI.generate` (ai.py) streams via `client.aio.models.generate_content_stream`; history `assistant` role maps to Gemini's `model` role. Attachments travel as provider-neutral blocks (`{"type":"bytes","mime","data"}` / `{"type":"text"}`) converted to `types.Part` there. Blocked/safety finishes set `Result.refused`; `MAX_TOKENS` sets `truncated`.
4. `LiveReply` (animations.py) sends a placeholder message and runs two background tasks: an edit loop every ~0.9 s (spinner/phrases while no text, then raw buffered text + `▍` cursor in plain text) and a typing chat-action loop. `finish()` splits the answer with `split_markdown` (never leaves a code fence open across chunks), converts each chunk with `md_to_html`, and falls back to plain text if Telegram rejects the HTML.
5. Errors map to localized messages in `error_key`; on any failure/refusal/stop-without-output the just-saved user turn is popped from history so turns stay alternating.

**Files mode** (`prompts.py` + `files.py` + `LiveReply(hide_stream=True)`): the system prompt tells the model to wrap output in `<file name="x.ext">…</file>`; `parse_files` extracts them, sanitizes filenames, converts `.docx` bodies from Markdown via python-docx, and `deliver` sends them as documents. While generating, users see a progress counter instead of raw file text. "📎 Save as file" under normal answers uses `answer_to_file`.

**Modes and prompts:** `prompts.py` `MODES` holds each mode's system prompt and `max_tokens`; `build_system(mode, style, lang)` composes base + mode + answer-length style + reply-language. Adding a mode requires: an entry in `MODES` and `MODE_ORDER`, `mode_<name>` and `hint_<name>` strings in every language in `i18n.py`, and (since `modes_kb` pairs buttons in twos) an even total count.

**i18n:** `i18n.py` `STRINGS[lang][key]` with `t(lang, key, **fmt)`; falls back to English. UI strings use Telegram HTML (`<b>`, `&amp;`). Every new key must be added to all three languages (en/ru/uz). The `thinking` key is a list of animation phrases, not a string. Callback data namespaces: `lang:`, `mode:`, `style:`, `act:`, `re:`, `stop`.

**Other notes:**
- `prompt_guide.html` is a standalone, self-contained page sent by `/guide`; its path is resolved relative to the repo root in `handlers.py`.
- Access control: `ALLOWED_USERS` is enforced by one outer middleware in `build_router` (empty = public). Per-user rate limiting lives in `App.rate_limited` and is checked in `run_task`. Logger levels for http libs are forced to WARNING in `main.py` so URLs/headers never get logged; keep secrets `field(repr=False)` in `Config`.
- DB: `users(lang, mode, style)` and `messages(role, content)`; `lang IS NULL` means the user hasn't chosen a language yet and every entry point must prompt for it (`ensure_lang`).
