from aiogram import types

from keyboards.default import BTN_CODE
from loader import dp
from utils.site_api import api
from .texts import answer_code


@dp.message_handler(commands=["kod", "code"], chat_type=types.ChatType.PRIVATE)
@dp.message_handler(text=BTN_CODE, chat_type=types.ChatType.PRIVATE)
async def new_code(message: types.Message):
    status, data = await api.code(message.from_user, message.chat.id)
    await answer_code(message, status, data)
