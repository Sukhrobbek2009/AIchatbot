from __future__ import annotations

from aiogram.types import InlineKeyboardButton as B
from aiogram.types import InlineKeyboardMarkup

from .i18n import LANGS, t
from .prompts import MODE_ORDER


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[B(text=label, callback_data=f"lang:{code}")] for code, label in LANGS.items()]
    )


def modes_kb(lang: str, current: str | None = None) -> InlineKeyboardMarkup:
    def label(m: str) -> str:
        text = t(lang, f"mode_{m}")
        return f"● {text}" if m == current else text

    rows = [
        [B(text=label(a), callback_data=f"mode:{a}"), B(text=label(b), callback_data=f"mode:{b}")]
        for a, b in zip(MODE_ORDER[::2], MODE_ORDER[1::2])
    ]
    rows.append([B(text=t(lang, "btn_new"), callback_data="act:new"),
                 B(text=t(lang, "btn_guide"), callback_data="act:guide")])
    rows.append([B(text=t(lang, "btn_settings"), callback_data="act:settings"),
                 B(text=t(lang, "btn_help"), callback_data="act:help")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def answer_kb(lang: str, with_file: bool = True) -> InlineKeyboardMarkup:
    row1 = [B(text=t(lang, "act_regen"), callback_data="re:regen"),
            B(text=t(lang, "act_short"), callback_data="re:short"),
            B(text=t(lang, "act_long"), callback_data="re:long")]
    row2 = []
    if with_file:
        row2.append(B(text=t(lang, "act_file"), callback_data="re:file"))
    row2 += [B(text=t(lang, "btn_new"), callback_data="act:new"),
             B(text=t(lang, "btn_menu"), callback_data="act:menu")]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])


def stop_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[B(text=t(lang, "btn_stop"), callback_data="stop")]])


def settings_kb(lang: str, style: str) -> InlineKeyboardMarkup:
    def s(name: str) -> B:
        text = t(lang, f"style_{name}")
        return B(text=f"● {text}" if name == style else text, callback_data=f"style:{name}")

    return InlineKeyboardMarkup(inline_keyboard=[
        [s("short"), s("normal"), s("detailed")],
        [B(text=t(lang, "btn_lang"), callback_data="act:lang"),
         B(text=t(lang, "btn_menu"), callback_data="act:menu")],
    ])
