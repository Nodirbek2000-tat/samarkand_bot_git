"""
Hammaga yuborish: saytdagi yangi material (rasm + qisqa matn + «Davomini o'qish») yoki /admin dagi reklama.

Sayt navbat tutadi (/api/bot/broadcasts); bot bittadan oladi va obunachilarni sahifama-sahifa yuradi:
* bir vaqtda BATCH ta xabar, har to'plam kamida 1 soniya — Telegram limiti (~30 xabar/soniya) ichida eng tez;
* rasm bir marta yuklanadi, keyin uning file_id si hammaga qayta ishlatiladi (trafik ham, vaqt ham tejaladi);
* har REPORT_EVERY soniyada sayt holat oladi (admin panelda jonli ko'rinadi) va "to'xtatildi" bo'lsa — to'xtaymiz;
* cursor saytda saqlanadi: bot qayta ishga tushsa, to'xtagan joyidan davom etadi (hech kimga ikki marta bormaydi).
"""
import asyncio
import io
import logging
from typing import Optional

from aiogram import Bot, types
from aiogram.utils import exceptions

from data import config
from utils.outbox import UNREACHABLE
from utils.site_api import SiteUnavailable, api

BATCH = 25
PAGE = 500
REPORT_EVERY = 3.0
IDLE = 3.0

OK, FAILED, BLOCKED = 0, 1, 2

_task: Optional[asyncio.Task] = None


class Sender:
    """Bitta yuborishning "qanday yuborish" qismi: reklama — nusxa, yangilik — rasm/matn + tugma."""

    def __init__(self, bot: Bot, b: dict):
        self.bot = bot
        self.b = b
        self.file_id: str = b.get("file_id") or ""
        self.photo: Optional[bytes] = None
        self.lock = asyncio.Lock()
        self.text, self.markup = self.compose()

    def compose(self):
        if self.b["kind"] == "ad":
            return "", None
        text = self.b.get("text") or ""
        url = f"{config.SITE_URL}{self.b['url']}" if self.b.get("url") else ""
        if url.startswith("https://"):
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📖 Davomini o'qish", url=url))
            return text, markup
        if url:  # Telegram https bo'lmagan (localhost) tugmani qabul qilmaydi — sinov paytida havola matnda
            text += f"\n\n🔗 {url}"
        return text, None

    async def prepare(self):
        if self.b["kind"] == "post" and self.b.get("photo") and not self.file_id:
            self.photo = await api.media(self.b["photo"])
            if self.photo is None:
                logging.warning("Rasm yuklab olinmadi (%s) — matn o'zi yuboriladi", self.b["photo"])

    async def __call__(self, chat_id: int):
        b = self.b
        if b["kind"] == "ad":
            return await self.bot.copy_message(chat_id, b["from_chat_id"], b["message_id"])
        if self.file_id:
            return await self.bot.send_photo(chat_id, self.file_id, caption=self.text, reply_markup=self.markup)
        if self.photo is None:
            return await self.bot.send_message(chat_id, self.text, reply_markup=self.markup, disable_web_page_preview=True)
        # rasm hali Telegramda yo'q: birinchi yuborish yuklaydi, qolganlar file_id ni kutadi
        async with self.lock:
            if not self.file_id:
                msg = await self.bot.send_photo(
                    chat_id, types.InputFile(io.BytesIO(self.photo), filename="cover.jpg"), caption=self.text, reply_markup=self.markup
                )
                self.file_id = msg.photo[-1].file_id
                return msg
        return await self.bot.send_photo(chat_id, self.file_id, caption=self.text, reply_markup=self.markup)


async def deliver(send: Sender, chat_id: int) -> int:
    for _ in range(3):
        try:
            await send(chat_id)
            return OK
        except exceptions.RetryAfter as exc:  # limitga tegdik — aytilgan vaqtcha kutib, qayta
            await asyncio.sleep(exc.timeout + 0.5)
        except UNREACHABLE:
            return BLOCKED
        except exceptions.TelegramAPIError as exc:
            logging.debug("Yuborilmadi %s: %s", chat_id, exc)
            return FAILED
    return FAILED


async def report(b: dict, send: Sender, counts: dict, cursor: int, done: bool = False) -> dict:
    data = {"sent": counts["sent"], "failed": counts["failed"], "blocked": counts["blocked"], "cursor": cursor, "done": done}
    if send.file_id and not b.get("file_id"):
        data["file_id"] = b["file_id"] = send.file_id
    try:
        status, res = await api.progress(b["id"], **data)
    except SiteUnavailable as exc:
        logging.warning("Yuborish holatini saytga yozib bo'lmadi: %s", exc)
        return {}
    if status == 200:  # yozildi — hisoblagichlar endi saytda
        counts.update(sent=0, failed=0, blocked=[])
        return res
    return {}


async def run(bot: Bot, b: dict) -> None:
    loop = asyncio.get_event_loop()
    send = Sender(bot, b)
    await send.prepare()
    counts = {"sent": 0, "failed": 0, "blocked": []}
    cursor = int(b.get("cursor") or 0)
    last = loop.time()
    stopped = False
    logging.info("Yuborish #%s boshlandi (%s)", b["id"], b["kind"])

    while not stopped:
        status, page = await api.subscribers(cursor, PAGE)
        items = page.get("items", []) if status == 200 else []
        if not items:
            break
        for i in range(0, len(items), BATCH):
            chunk = items[i : i + BATCH]
            started = loop.time()
            results = await asyncio.gather(*(deliver(send, chat_id) for _, chat_id in chunk))
            for (_, chat_id), res in zip(chunk, results):
                if res == OK:
                    counts["sent"] += 1
                else:
                    counts["failed"] += 1
                    if res == BLOCKED:
                        counts["blocked"].append(chat_id)
            cursor = chunk[-1][0]
            if loop.time() - last >= REPORT_EVERY:
                last = loop.time()
                if (await report(b, send, counts, cursor)).get("status") == "cancelled":
                    stopped = True
                    break
            await asyncio.sleep(max(0.0, 1.0 - (loop.time() - started)))

    final = await report(b, send, counts, cursor, done=not stopped)
    logging.info("Yuborish #%s tugadi: %s", b["id"], final)
    if b.get("created_by_chat") and final:
        state = "✅ Reklama yuborildi." if not stopped else "⏹ Reklama to'xtatildi."
        text = (
            f"{state}\n\n"
            f"📨 Yetkazildi: <b>{final.get('sent', 0)}</b>\n"
            f"🚫 Yetkazilmadi: <b>{final.get('failed', 0)}</b>\n"
            f"👥 Jami: {final.get('total', 0)}"
        )
        try:
            await bot.send_message(b["created_by_chat"], text)
        except exceptions.TelegramAPIError:
            pass


async def worker(bot: Bot) -> None:
    while True:
        try:
            status, data = await api.next_broadcast()
            b = data.get("broadcast") if status == 200 else None
            if b:
                await run(bot, b)
                continue  # navbatda yana bo'lsa — darhol
        except SiteUnavailable:
            pass  # outbox worker allaqachon logga yozadi
        except asyncio.CancelledError:
            raise
        except Exception:  # bitta xato butun yuboruvchini to'xtatmasin
            logging.exception("Yuboruvchi xatosi")
        await asyncio.sleep(IDLE)


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
