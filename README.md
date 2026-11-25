# AI Telegram Bot

A Telegram AI assistant powered by Google Gemini, built with Python + aiogram 3.

**Features**
- Live "typing" animation: animated spinner while thinking, then text streams in with a cursor
- 8 modes: Chat, Code, Files, Translate, Summarize, Writer, Tutor, Analyze
- Generates downloadable files (code, CSV, JSON, Markdown, Word `.docx`)
- Reads photos, PDFs and text/code files (send with a caption as the question)
- Languages: English, Русский, O'zbekcha (add more in `bot/i18n.py`)
- Buttons: mode menu, ⏹ Stop, 🔄 Redo, ✂️ Shorter, 📖 Detailed, 📎 Save as file, 🧹 New chat, ⚙️ Settings
- `/guide` sends `prompt_guide.html` (prompt-writing guide with a prompt builder)
- Per-user history in SQLite, per-user locking, optional allow-list

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# .env already exists (git-ignored): fill BOT_TOKEN and GEMINI_API_KEY
python run.py
```
- `BOT_TOKEN`: create a bot with [@BotFather](https://t.me/BotFather)
- `GEMINI_API_KEY`: from https://aistudio.google.com/apikey
- `MODEL` defaults to `gemini-2.5-flash`; set e.g. a Pro model for harder tasks
- `RATE_LIMIT_PER_MIN` caps requests per user (default 12)
- `ALLOWED_USERS`: comma-separated Telegram IDs to keep the bot private

## Layout
```
run.py               entry point
prompt_guide.html    standalone prompt guide
bot/
  main.py            startup, command menu, polling
  handlers.py        commands, buttons, message/photo/document handling, generation pipeline
  ai.py              streaming Gemini call
  animations.py      LiveReply: spinner + streaming edits
  formatting.py      Markdown -> Telegram HTML, safe message splitting
  files.py           <file> parsing, .docx builder
  prompts.py         per-mode system prompts and token limits
  i18n.py            translations
  keyboards.py       inline keyboards
  db.py              SQLite storage
```

## Notes
- Runs with long polling (no public server needed). Keep the process alive with systemd, Docker or `pm2`.
- Security: `.env` is git-ignored (keep it `chmod 600`), SQLite history is stored with owner-only permissions, per-user rate limiting, optional `ALLOWED_USERS` allow-list enforced by one middleware.
