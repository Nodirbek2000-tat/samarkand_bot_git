from aiogram import types

from keyboards.default import contact_keyboard
from loader import dp
from utils.site_api import api
from .texts import ASK_OWN_PHONE, answer_code


@dp.message_handler(content_types=types.ContentType.CONTACT, chat_type=types.ChatType.PRIVATE)
async def got_contact(message: types.Message):
    contact = message.contact
    # faqat o'z raqami: boshqa odamning kontaktini yuborib ro'yxatdan o'tib bo'lmaydi
    if contact.user_id != message.from_user.id:
        await message.answer(ASK_OWN_PHONE, reply_markup=contact_keyboard)
        return

    status, data = await api.register(message.from_user, contact, message.chat.id)
    if data.get("created"):
        await message.answer(f"✅ Ro'yxatdan o'tdingiz, <b>{data.get('name') or message.from_user.first_name}</b>!")
    await answer_code(message, status, data)
