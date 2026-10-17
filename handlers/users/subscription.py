from aiogram import types
from aiogram.utils.exceptions import MessageNotModified, TelegramAPIError

from keyboards.inline.admin import SUB_CHECK, subscribe_keyboard
from loader import dp
from middlewares.audience import subscribe_text
from utils import audience
from utils.site_api import api
from .texts import answer_code


@dp.callback_query_handler(text=SUB_CHECK, state="*")
async def check_subscription(call: types.CallbackQuery):
    missing = await audience.missing_channels(call.bot, call.from_user.id)
    if missing:
        await call.answer("❌ Hali hamma kanallarga obuna bo'lmadingiz", show_alert=True)
        try:
            await call.message.edit_text(subscribe_text(missing), reply_markup=subscribe_keyboard(missing))
        except (MessageNotModified, TelegramAPIError):
            pass
        return
    await call.answer("✅ Rahmat!")
    try:
        await call.message.delete()
    except TelegramAPIError:
        pass
    # obuna tasdiqlandi — /start bosgandagi kabi davom etamiz
    status, data = await api.code(call.from_user, call.message.chat.id)
    await answer_code(call.message, status, data)
