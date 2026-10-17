from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils import broadcaster, outbox
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.site_api import api


async def on_startup(dispatcher):
    # Birlamchi komandalar (/start, /kod, /help)
    await set_default_commands(dispatcher)

    # Sayt navbatga qo'ygan xabarlarni yetkazish (murojaatlarga javoblar va h.k.) + saytga "tirikman" signali
    outbox.start(dispatcher.bot)

    # Hammaga yuborish: saytdagi yangi materiallar va /admin dagi reklama
    broadcaster.start(dispatcher.bot)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


async def on_shutdown(dispatcher):
    await broadcaster.stop()
    await outbox.stop()
    await api.close()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
