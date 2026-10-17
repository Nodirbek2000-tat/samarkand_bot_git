"""
Har bir shaxsiy xabar/tugma bosishda:
1) foydalanuvchi saytdagi obunachilar ro'yxatiga yoziladi (keshlangan, ortiqcha so'rovsiz);
2) majburiy kanallarga obuna tekshiriladi — obuna bo'lmaguncha botning boshqa funksiyalari ishlamaydi.
Adminlar va "✅ Obuna bo'ldim" tugmasining o'zi tekshiruvdan ozod.
"""
from html import escape

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from keyboards.inline.admin import SUB_CHECK, subscribe_keyboard
from utils import audience


def subscribe_text(channels) -> str:
    names = "\n".join(f"• <b>{escape(ch.get('title') or ch.get('username') or 'Kanal')}</b>" for ch in channels)
    return (
        "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n"
        f"{names}\n\n"
        "Obuna bo'lgach, <b>«✅ Obuna bo'ldim»</b> tugmasini bosing."
    )


class AudienceMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if message.chat.type != types.ChatType.PRIVATE or not message.from_user:
            return
        if await audience.touch(message.from_user, message.chat.id):
            return  # admin
        missing = await audience.missing_channels(message.bot, message.from_user.id)
        if missing:
            await message.answer(subscribe_text(missing), reply_markup=subscribe_keyboard(missing))
            raise CancelHandler()

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        if not call.message or call.message.chat.type != types.ChatType.PRIVATE:
            return
        if await audience.touch(call.from_user, call.message.chat.id) or call.data == SUB_CHECK:
            return
        missing = await audience.missing_channels(call.bot, call.from_user.id)
        if missing:
            await call.answer("Avval kanallarga obuna bo'ling", show_alert=True)
            await call.message.answer(subscribe_text(missing), reply_markup=subscribe_keyboard(missing))
            raise CancelHandler()
