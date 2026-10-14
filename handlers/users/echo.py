from aiogram import types

from keyboards.default import main_keyboard
from loader import dp


# Qolgan barcha xabarlar: bot nima qilishini eslatamiz (eng oxirida ro'yxatdan o'tadi)
@dp.message_handler(state=None, chat_type=types.ChatType.PRIVATE, content_types=types.ContentTypes.ANY)
async def bot_echo(message: types.Message):
    await message.answer(
        "Saytga kirish kodi kerak bo'lsa — <b>«🔑 Yangi kod olish»</b> tugmasini bosing.",
        reply_markup=main_keyboard,
    )
