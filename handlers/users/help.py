from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from keyboards.default import BTN_HELP, main_keyboard
from loader import dp
from .texts import help_text


@dp.message_handler(CommandHelp(), chat_type=types.ChatType.PRIVATE)
@dp.message_handler(text=BTN_HELP, chat_type=types.ChatType.PRIVATE)
async def bot_help(message: types.Message):
    await message.answer(help_text(), reply_markup=main_keyboard, disable_web_page_preview=True)
