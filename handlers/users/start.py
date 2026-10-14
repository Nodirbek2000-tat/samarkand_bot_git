from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.site_api import api
from .texts import answer_code


@dp.message_handler(CommandStart(), chat_type=types.ChatType.PRIVATE)
async def bot_start(message: types.Message):
    # ro'yxatdan o'tgan bo'lsa — darhol kod; bo'lmasa sayt 404 qaytaradi va raqam so'raymiz
    status, data = await api.code(message.from_user, message.chat.id)
    await answer_code(message, status, data)
