"""Translations. Add a language by adding a block to STRINGS and LANGS."""
from __future__ import annotations

LANGS = {"en": "🇬🇧 English", "ru": "🇷🇺 Русский", "uz": "🇺🇿 O'zbekcha"}
DEFAULT_LANG = "en"

STRINGS: dict[str, dict] = {
    "en": {
        "choose_lang": "🌍 <b>Choose your language</b>\nВыберите язык · Tilni tanlang",
        "welcome": (
            "👋 Hi, <b>{name}</b>! I'm your AI assistant.\n\n"
            "I can answer questions, write &amp; debug code, generate files, translate, "
            "summarize documents and read images or PDFs.\n\n"
            "Pick a mode below, or just type your message 👇"
        ),
        "menu": "✨ <b>Main menu</b>\nCurrent mode: <b>{mode}</b>",
        "mode_chat": "💬 Chat", "mode_code": "👨‍💻 Code", "mode_files": "📄 Files",
        "mode_translate": "🌐 Translate", "mode_summarize": "📝 Summarize",
        "mode_write": "✍️ Writer", "mode_learn": "🎓 Tutor", "mode_analyze": "🔬 Analyze",
        "hint_chat": "Ask me anything.",
        "hint_code": "Describe what to build or paste code to fix/explain.",
        "hint_files": "Tell me what file you need (e.g. “a CV in Word”, “a Python script”, “a CSV of …”).",
        "hint_translate": "Send text to translate. Add the target language, e.g. “to German: …”.",
        "hint_summarize": "Send a long text, article, or upload a PDF/TXT file.",
        "hint_write": "Tell me what to write, or paste text to improve.",
        "hint_learn": "Name a topic you want to understand.",
        "hint_analyze": "Send data, a photo, screenshot or PDF and ask your question.",
        "mode_set": "✅ Mode: <b>{mode}</b>\n{hint}",
        "btn_new": "🧹 New chat", "btn_lang": "🌍 Language", "btn_guide": "📘 Prompt guide",
        "btn_settings": "⚙️ Settings", "btn_help": "❓ Help", "btn_menu": "🏠 Menu",
        "btn_stop": "⏹ Stop",
        "act_regen": "🔄 Redo", "act_short": "✂️ Shorter", "act_long": "📖 Detailed",
        "act_file": "📎 Save as file",
        "new_done": "🧹 Done — fresh conversation started.",
        "lang_set": "✅ Language set to English.",
        "settings": "⚙️ <b>Settings</b>\nAnswer length: <b>{style}</b>\nLanguage: <b>{lang}</b>",
        "style_short": "⚡ Short", "style_normal": "⚖️ Normal", "style_detailed": "📚 Detailed",
        "style_label_short": "short", "style_label_normal": "normal", "style_label_detailed": "detailed",
        "help": (
            "❓ <b>How to use</b>\n\n"
            "• Just type a message — I answer with a live typing animation.\n"
            "• <b>Modes</b> tune me for a job: Chat, Code, Files, Translate, Summarize, Writer, Tutor, Analyze.\n"
            "• Send a <b>photo</b>, <b>PDF</b> or text/code <b>file</b> and add a question as the caption.\n"
            "• Under each answer: 🔄 redo, ✂️ shorter, 📖 more detail, 📎 save as file.\n"
            "• ⏹ stops an answer mid-way.\n\n"
            "<b>Commands</b>\n/menu · /new · /mode · /lang · /settings · /guide · /help"
        ),
        "guide_caption": "📘 <b>Prompt guide</b> — open the file in your browser for tips, templates and examples.",
        "thinking": ["Thinking", "Reading your message", "Working on it", "Almost there"],
        "writing_file": "Writing your file",
        "busy": "⏳ I'm still answering your previous message. Tap ⏹ Stop or wait a moment.",
        "stopped": "⏹ Stopped.",
        "stopped_note": "⏹ <i>stopped</i>",
        "truncated": "⚠️ <i>The answer was cut at the length limit. Say “continue” to get the rest.</i>",
        "refused": "🚫 I can't help with that request. Try rephrasing it.",
        "err_generic": "😕 Something went wrong. Please try again in a moment.",
        "err_rate": "🚦 I'm getting too many requests right now. Please retry in a few seconds.",
        "err_overloaded": "🔥 The AI service is overloaded. Please retry shortly.",
        "err_ratelimit": "🐢 You're sending messages too fast. Please wait a few seconds.",
        "err_config": "🔧 The bot is not configured correctly (API access). Details are in the admin logs.",
        "file_ready": "📎 Here you go!",
        "file_none": "🤔 Nothing to save yet — ask me something first.",
        "unsupported": "🙈 I can't read that type of message yet. Send text, a photo, a PDF or a text/code file.",
        "too_big": "📦 That file is too large (max {mb} MB).",
        "not_allowed": "🔒 This bot is private.",
        "img_default": "Describe this image and point out anything important.",
        "doc_default": "Summarize this document.",
        "cmd_start": "Start the bot", "cmd_menu": "Open the main menu", "cmd_new": "Start a new chat",
        "cmd_mode": "Choose a mode", "cmd_lang": "Change language", "cmd_settings": "Settings",
        "cmd_guide": "Prompt guide (HTML)", "cmd_help": "Help",
    },
    "ru": {
        "choose_lang": "🌍 <b>Выберите язык</b>\nChoose your language · Tilni tanlang",
        "welcome": (
            "👋 Привет, <b>{name}</b>! Я твой ИИ-ассистент.\n\n"
            "Отвечаю на вопросы, пишу и чиню код, создаю файлы, перевожу, "
            "делаю выжимки из документов и понимаю фото и PDF.\n\n"
            "Выбери режим ниже или просто напиши сообщение 👇"
        ),
        "menu": "✨ <b>Главное меню</b>\nТекущий режим: <b>{mode}</b>",
        "mode_chat": "💬 Чат", "mode_code": "👨‍💻 Код", "mode_files": "📄 Файлы",
        "mode_translate": "🌐 Перевод", "mode_summarize": "📝 Выжимка",
        "mode_write": "✍️ Тексты", "mode_learn": "🎓 Репетитор", "mode_analyze": "🔬 Анализ",
        "hint_chat": "Спрашивай что угодно.",
        "hint_code": "Опиши, что создать, или пришли код для исправления/разбора.",
        "hint_files": "Скажи, какой файл нужен («резюме в Word», «скрипт на Python», «CSV с …»).",
        "hint_translate": "Пришли текст для перевода. Можно указать язык: «на немецкий: …».",
        "hint_summarize": "Пришли длинный текст, статью или загрузи PDF/TXT.",
        "hint_write": "Скажи, что написать, или пришли текст для улучшения.",
        "hint_learn": "Назови тему, которую хочешь понять.",
        "hint_analyze": "Пришли данные, фото, скриншот или PDF и задай вопрос.",
        "mode_set": "✅ Режим: <b>{mode}</b>\n{hint}",
        "btn_new": "🧹 Новый чат", "btn_lang": "🌍 Язык", "btn_guide": "📘 Гайд по промптам",
        "btn_settings": "⚙️ Настройки", "btn_help": "❓ Помощь", "btn_menu": "🏠 Меню",
        "btn_stop": "⏹ Стоп",
        "act_regen": "🔄 Заново", "act_short": "✂️ Короче", "act_long": "📖 Подробнее",
        "act_file": "📎 В файл",
        "new_done": "🧹 Готово — начат новый диалог.",
        "lang_set": "✅ Язык: русский.",
        "settings": "⚙️ <b>Настройки</b>\nДлина ответа: <b>{style}</b>\nЯзык: <b>{lang}</b>",
        "style_short": "⚡ Коротко", "style_normal": "⚖️ Обычно", "style_detailed": "📚 Подробно",
        "style_label_short": "коротко", "style_label_normal": "обычно", "style_label_detailed": "подробно",
        "help": (
            "❓ <b>Как пользоваться</b>\n\n"
            "• Просто напиши сообщение — отвечаю с живой анимацией печати.\n"
            "• <b>Режимы</b> настраивают меня под задачу: Чат, Код, Файлы, Перевод, Выжимка, Тексты, Репетитор, Анализ.\n"
            "• Отправь <b>фото</b>, <b>PDF</b> или текстовый/кодовый <b>файл</b> и добавь вопрос в подпись.\n"
            "• Под ответом: 🔄 заново, ✂️ короче, 📖 подробнее, 📎 в файл.\n"
            "• ⏹ останавливает ответ.\n\n"
            "<b>Команды</b>\n/menu · /new · /mode · /lang · /settings · /guide · /help"
        ),
        "guide_caption": "📘 <b>Гайд по промптам</b> — открой файл в браузере: советы, шаблоны и примеры.",
        "thinking": ["Думаю", "Читаю сообщение", "Работаю над ответом", "Почти готово"],
        "writing_file": "Пишу файл",
        "busy": "⏳ Я ещё отвечаю на предыдущее сообщение. Нажми ⏹ Стоп или подожди.",
        "stopped": "⏹ Остановлено.",
        "stopped_note": "⏹ <i>остановлено</i>",
        "truncated": "⚠️ <i>Ответ обрезан по лимиту длины. Напиши «продолжай», чтобы получить остальное.</i>",
        "refused": "🚫 С этим запросом я помочь не могу. Попробуй переформулировать.",
        "err_generic": "😕 Что-то пошло не так. Попробуй ещё раз чуть позже.",
        "err_rate": "🚦 Сейчас слишком много запросов. Повтори через несколько секунд.",
        "err_overloaded": "🔥 Сервис ИИ перегружен. Повтори чуть позже.",
        "err_ratelimit": "🐢 Слишком много сообщений подряд. Подожди несколько секунд.",
        "err_config": "🔧 Бот настроен неверно (доступ к API). Подробности — в логах администратора.",
        "file_ready": "📎 Держи!",
        "file_none": "🤔 Пока нечего сохранять — сначала задай вопрос.",
        "unsupported": "🙈 Такой тип сообщений я пока не читаю. Пришли текст, фото, PDF или текстовый/кодовый файл.",
        "too_big": "📦 Файл слишком большой (макс. {mb} МБ).",
        "not_allowed": "🔒 Этот бот приватный.",
        "img_default": "Опиши это изображение и выдели главное.",
        "doc_default": "Сделай краткую выжимку этого документа.",
        "cmd_start": "Запустить бота", "cmd_menu": "Главное меню", "cmd_new": "Новый чат",
        "cmd_mode": "Выбрать режим", "cmd_lang": "Сменить язык", "cmd_settings": "Настройки",
        "cmd_guide": "Гайд по промптам (HTML)", "cmd_help": "Помощь",
    },
    "uz": {
        "choose_lang": "🌍 <b>Tilni tanlang</b>\nChoose your language · Выберите язык",
        "welcome": (
            "👋 Salom, <b>{name}</b>! Men sizning AI yordamchingizman.\n\n"
            "Savollarga javob beraman, kod yozaman va tuzataman, fayllar yarataman, tarjima qilaman, "
            "hujjatlarni qisqartiraman, rasm va PDF'larni o'qiyman.\n\n"
            "Quyidan rejimni tanlang yoki shunchaki xabar yozing 👇"
        ),
        "menu": "✨ <b>Asosiy menyu</b>\nJoriy rejim: <b>{mode}</b>",
        "mode_chat": "💬 Suhbat", "mode_code": "👨‍💻 Kod", "mode_files": "📄 Fayllar",
        "mode_translate": "🌐 Tarjima", "mode_summarize": "📝 Qisqacha",
        "mode_write": "✍️ Yozuvchi", "mode_learn": "🎓 Ustoz", "mode_analyze": "🔬 Tahlil",
        "hint_chat": "Xohlagan narsangizni so'rang.",
        "hint_code": "Nima yaratish kerakligini yozing yoki tuzatish uchun kod yuboring.",
        "hint_files": "Qanday fayl kerakligini ayting (“Word'da CV”, “Python skript”, “… CSV”).",
        "hint_translate": "Tarjima uchun matn yuboring. Tilni ko'rsating: “nemis tiliga: …”.",
        "hint_summarize": "Uzun matn, maqola yuboring yoki PDF/TXT yuklang.",
        "hint_write": "Nima yozish kerakligini ayting yoki yaxshilash uchun matn yuboring.",
        "hint_learn": "Tushunmoqchi bo'lgan mavzuni ayting.",
        "hint_analyze": "Ma'lumot, rasm, skrinshot yoki PDF yuboring va savol bering.",
        "mode_set": "✅ Rejim: <b>{mode}</b>\n{hint}",
        "btn_new": "🧹 Yangi suhbat", "btn_lang": "🌍 Til", "btn_guide": "📘 Prompt qo'llanma",
        "btn_settings": "⚙️ Sozlamalar", "btn_help": "❓ Yordam", "btn_menu": "🏠 Menyu",
        "btn_stop": "⏹ To'xtatish",
        "act_regen": "🔄 Qayta", "act_short": "✂️ Qisqaroq", "act_long": "📖 Batafsil",
        "act_file": "📎 Faylga",
        "new_done": "🧹 Tayyor — yangi suhbat boshlandi.",
        "lang_set": "✅ Til: o'zbekcha.",
        "settings": "⚙️ <b>Sozlamalar</b>\nJavob uzunligi: <b>{style}</b>\nTil: <b>{lang}</b>",
        "style_short": "⚡ Qisqa", "style_normal": "⚖️ O'rtacha", "style_detailed": "📚 Batafsil",
        "style_label_short": "qisqa", "style_label_normal": "o'rtacha", "style_label_detailed": "batafsil",
        "help": (
            "❓ <b>Qanday foydalanish</b>\n\n"
            "• Shunchaki xabar yozing — men jonli yozish animatsiyasi bilan javob beraman.\n"
            "• <b>Rejimlar</b> meni vazifaga moslaydi: Suhbat, Kod, Fayllar, Tarjima, Qisqacha, Yozuvchi, Ustoz, Tahlil.\n"
            "• <b>Rasm</b>, <b>PDF</b> yoki matn/kod <b>fayl</b> yuboring va savolni izohga yozing.\n"
            "• Har bir javob ostida: 🔄 qayta, ✂️ qisqaroq, 📖 batafsil, 📎 faylga.\n"
            "• ⏹ javobni to'xtatadi.\n\n"
            "<b>Buyruqlar</b>\n/menu · /new · /mode · /lang · /settings · /guide · /help"
        ),
        "guide_caption": "📘 <b>Prompt qo'llanma</b> — faylni brauzerda oching: maslahatlar, shablonlar va misollar.",
        "thinking": ["O'ylayapman", "Xabarni o'qiyapman", "Javob tayyorlayapman", "Deyarli tayyor"],
        "writing_file": "Faylni yozyapman",
        "busy": "⏳ Oldingi xabaringizga hali javob yozyapman. ⏹ To'xtatish tugmasini bosing yoki kuting.",
        "stopped": "⏹ To'xtatildi.",
        "stopped_note": "⏹ <i>to'xtatildi</i>",
        "truncated": "⚠️ <i>Javob uzunlik chegarasida uzildi. Davomini olish uchun “davom et” deb yozing.</i>",
        "refused": "🚫 Bu so'rov bo'yicha yordam bera olmayman. Boshqacha ifodalab ko'ring.",
        "err_generic": "😕 Nimadir xato ketdi. Birozdan keyin qayta urinib ko'ring.",
        "err_rate": "🚦 Hozir so'rovlar juda ko'p. Bir necha soniyadan keyin qayta urining.",
        "err_overloaded": "🔥 AI xizmati band. Birozdan keyin qayta urining.",
        "err_ratelimit": "🐢 Xabarlar juda tez yuborilyapti. Bir necha soniya kuting.",
        "err_config": "🔧 Bot noto'g'ri sozlangan (API ruxsati). Tafsilotlar admin jurnalida.",
        "file_ready": "📎 Marhamat!",
        "file_none": "🤔 Hozircha saqlash uchun narsa yo'q — avval savol bering.",
        "unsupported": "🙈 Bunday xabar turini hali o'qiy olmayman. Matn, rasm, PDF yoki matn/kod fayl yuboring.",
        "too_big": "📦 Fayl juda katta (maks. {mb} MB).",
        "not_allowed": "🔒 Bu bot yopiq.",
        "img_default": "Bu rasmni tasvirlab bering va muhim narsalarni ko'rsating.",
        "doc_default": "Bu hujjatni qisqacha bayon qiling.",
        "cmd_start": "Botni ishga tushirish", "cmd_menu": "Asosiy menyu", "cmd_new": "Yangi suhbat",
        "cmd_mode": "Rejimni tanlash", "cmd_lang": "Tilni o'zgartirish", "cmd_settings": "Sozlamalar",
        "cmd_guide": "Prompt qo'llanma (HTML)", "cmd_help": "Yordam",
    },
}


def t(lang: str | None, key: str, **kw):
    table = STRINGS.get(lang or DEFAULT_LANG, STRINGS[DEFAULT_LANG])
    val = table.get(key, STRINGS[DEFAULT_LANG].get(key, key))
    if kw and isinstance(val, str):
        return val.format(**kw)
    return val
