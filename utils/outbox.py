"""
Sayt navbatga qo'ygan xabarlarni yetkazish (murojaatlarga javob va h.k.).

Har OUTBOX_INTERVAL soniyada /api/bot/outbox so'raladi — bu saytga "bot tirik" degan signal ham.
Har bir xabar natijasi /ack bilan qaytariladi: yuborildi / xato (sayt 5 martagacha qayta urinadi) /
foydalanuvchi botni bloklagan.
"""
import asyncio
import logging
from typing import Optional

from aiogram import Bot
from aiogram.utils import exceptions

from data import config
from utils.site_api import SiteUnavailable, api

_task: Optional[asyncio.Task] = None

# foydalanuvchiga endi umuman yetib bo'lmaydigan holatlar (umumiy Unauthorized emas — u noto'g'ri token ham bo'lishi mumkin)
UNREACHABLE = (
    exceptions.BotBlocked,
    exceptions.UserDeactivated,
    exceptions.CantInitiateConversation,
    exceptions.BotKicked,
    exceptions.ChatNotFound,
)


async def deliver(bot: Bot, msg: dict) -> None:
    try:
        await bot.send_message(msg["chat_id"], msg["text"], disable_web_page_preview=True)
    except exceptions.RetryAfter as exc:  # Telegram limiti — kutib, keyingi aylanishda qayta
        logging.warning("Telegram limit: %s soniya kutamiz", exc.timeout)
        await asyncio.sleep(exc.timeout)
        return
    except UNREACHABLE as exc:
        await api.ack(msg["id"], ok=False, error=str(exc), blocked=True)
        return
    except exceptions.TelegramAPIError as exc:
        await api.ack(msg["id"], ok=False, error=str(exc))
        return
    await api.ack(msg["id"], ok=True)


async def worker(bot: Bot) -> None:
    greeted = False
    site_down = False
    while True:
        try:
            if not greeted:
                # sayt bot username'ini shundan biladi (/kirish sahifasidagi havola uchun)
                status, _ = await api.hello(await bot.get_me())
                greeted = status == 200
            status, data = await api.outbox()
            if site_down:
                logging.info("Sayt bilan aloqa tiklandi")
                site_down = False
            for msg in data.get("messages", []) if status == 200 else []:
                await deliver(bot, msg)
                await asyncio.sleep(0.05)  # Telegram: sekundiga ~30 xabardan oshmaslik
        except SiteUnavailable as exc:
            if not site_down:
                logging.warning("Sayt javob bermayapti, kutyapman: %s", exc)
                site_down = True
                greeted = False
        except asyncio.CancelledError:
            raise
        except Exception:  # bitta xato butun workerni to'xtatmasin
            logging.exception("Outbox worker xatosi")
        await asyncio.sleep(config.OUTBOX_INTERVAL)


def start(bot: Bot) -> None:
    global _task
    _task = asyncio.get_event_loop().create_task(worker(bot))


async def stop() -> None:
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
