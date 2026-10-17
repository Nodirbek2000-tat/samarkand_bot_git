from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# callback_data qiymatlari — bir joyda
HOME = "adm:home"
STATS = "adm:stats"
CHANNELS = "adm:channels"
CHANNEL_ADD = "adm:chadd"
CHANNEL_DEL = "adm:chdel:"  # + kanal chat_id
AD = "adm:ad"
AD_SEND = "adm:adsend"
AD_CANCEL = "adm:adcancel"
SUB_CHECK = "sub:check"

BACK = InlineKeyboardButton("⬅️ Orqaga", callback_data=HOME)


def panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("📊 Statistika", callback_data=STATS),
        InlineKeyboardButton("📢 Majburiy kanallar", callback_data=CHANNELS),
        InlineKeyboardButton("📣 Reklama yuborish", callback_data=AD),
    )


def back_keyboard(to: str = HOME) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Orqaga", callback_data=to))


def channels_keyboard(channels: List[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        kb.add(InlineKeyboardButton(f"❌ {ch.get('title') or ch.get('username') or ch['chat_id']}", callback_data=f"{CHANNEL_DEL}{ch['chat_id']}"))
    kb.add(InlineKeyboardButton("➕ Kanal qo'shish", callback_data=CHANNEL_ADD))
    kb.add(BACK)
    return kb


def ad_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("✅ Yuborish", callback_data=AD_SEND),
        InlineKeyboardButton("❌ Bekor qilish", callback_data=AD_CANCEL),
    )


def subscribe_keyboard(channels: List[dict]) -> InlineKeyboardMarkup:
    """Majburiy obuna: har kanalga tugma + "Tekshirish"."""
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        if ch.get("link"):
            kb.add(InlineKeyboardButton(f"➕ {ch.get('title') or ch.get('username') or 'Kanal'}", url=ch["link"]))
    kb.add(InlineKeyboardButton("✅ Obuna bo'ldim", callback_data=SUB_CHECK))
    return kb
