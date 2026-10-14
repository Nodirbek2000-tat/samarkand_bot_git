"""Foydalanuvchiga ko'rinadigan matnlar va kod javobini chiqarish — bir joyda."""
import logging

from aiogram import types

from data import config
from keyboards.default import contact_keyboard, main_keyboard

WELCOME = (
    "Assalomu alaykum! 👋\n\n"
    "<b>«Yangi Samarqand»</b> — Samarqand viloyati tadbirkorlari jamoat maslahat kengashi boti.\n\n"
    "Saytda ro'yxatdan o'tish uchun pastdagi <b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing — "
    "bot sizga saytga kirish kodini beradi."
)

ASK_OWN_PHONE = "Iltimos, <b>o'zingizning</b> raqamingizni yuboring — pastdagi tugmani bosing."

BLOCKED = "⛔ Hisobingiz vaqtincha bloklangan. Iltimos, Kengash bilan bog'laning."

SITE_ERROR = "⚠️ Sayt bilan aloqa vaqtincha yo'q. Iltimos, birozdan keyin qayta urinib ko'ring."


def help_text() -> str:
    lines = [
        "<b>«Yangi Samarqand» boti</b>\n",
        "1️⃣ Saytda <b>«Kirish»</b> tugmasini bosing.",
        "2️⃣ Shu botda <b>«🔑 Yangi kod olish»</b> tugmasini bosing.",
        "3️⃣ Bot yuborgan 6 xonali kodni saytga kiriting.\n",
        "Kod 5 daqiqa amal qiladi va faqat bir marta ishlaydi.",
        "Saytdan yuborgan murojaatlaringizga javoblar ham shu botga keladi.",
    ]
    if config.SITE_URL.startswith("https://"):
        lines.append(f"\n🌐 Sayt: {config.SITE_URL}")
    return "\n".join(lines)


def code_text(code: str, ttl: int) -> str:
    minutes = max(1, ttl // 60)
    text = (
        "🔐 <b>Saytga kirish kodi:</b>\n\n"
        f"<code>{code[:3]} {code[3:]}</code>\n\n"
        f"Kodni saytdagi maydonga kiriting. U <b>{minutes} daqiqa</b> amal qiladi va faqat bir marta ishlaydi.\n"
        "⚠️ Kodni hech kimga bermang — Kengash xodimlari uni hech qachon so'ramaydi."
    )
    if config.SITE_URL.startswith("https://"):  # Telegram localhost havolalarini qabul qilmaydi
        text += f'\n\n🌐 <a href="{config.SITE_URL}/kirish">Saytdagi kirish sahifasi</a>'
    return text


async def answer_code(message: types.Message, status: int, data: dict) -> None:
    """Saytdan kelgan /bot/register yoki /bot/code javobini foydalanuvchiga tushunarli qilib chiqaradi."""
    if status == 200:
        await message.answer(
            code_text(data["code"], data.get("ttl", 300)), reply_markup=main_keyboard, disable_web_page_preview=True
        )
    elif status == 404:
        await message.answer(WELCOME, reply_markup=contact_keyboard)
    elif status == 429:
        await message.answer(
            f"⏳ Kod hozirgina yuborildi. Yangisini <b>{data.get('retry_after', 30)} soniyadan</b> keyin oling.\n"
            "Oldingi kod hali ham ishlaydi.",
            reply_markup=main_keyboard,
        )
    elif status == 403 and data.get("detail") == "blocked":
        await message.answer(BLOCKED)
    else:
        logging.error("Sayt kutilmagan javob qaytardi: %s %s", status, data)
        await message.answer(SITE_ERROR, reply_markup=main_keyboard)
