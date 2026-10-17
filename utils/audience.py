"""
Obunachilar, adminlar va majburiy kanallar — tez ishlashi uchun xotirada keshlanadi.

* touch(): foydalanuvchini saytdagi obunachilar ro'yxatiga yozadi (har 10 daqiqada ko'pi bilan bir marta)
  va u /admin ochishi mumkinmi — shu javobni eslab qoladi.
* missing_channels(): foydalanuvchi obuna bo'lmagan majburiy kanallar. Kanallar ro'yxati 60 soniya,
  "hammasiga obuna" natijasi esa 5 daqiqa keshlanadi — har xabarda Telegramga so'rov ketmaydi.
"""
import asyncio
import logging
import time
from typing import Dict, List, Tuple

from aiogram import Bot, types
from aiogram.utils.exceptions import TelegramAPIError

from data import config
from utils.site_api import SiteUnavailable, api

SEEN_TTL = 600  # obunachi ma'lumotini qayta yuborish oralig'i
ADMIN_TTL = 300  # admin huquqi o'zgarsa, ko'pi bilan 5 daqiqada bilinadi (/admin buyrug'i esa darhol tekshiradi)
CHANNELS_TTL = 60
MEMBER_OK_TTL = 300

OWNERS = {int(x) for x in config.ADMINS if str(x).lstrip("-").isdigit()}  # .env dagi ADMINS — har doim admin

_seen: Dict[int, float] = {}
_admin: Dict[int, Tuple[bool, float]] = {}
_channels: Tuple[List[dict], float] = ([], 0.0)
_member_ok: Dict[int, float] = {}


async def touch(user: types.User, chat_id: int, force: bool = False) -> bool:
    """Obunachini yangilaydi va admin ekanini qaytaradi. Sayt ishlamasa — oxirgi ma'lum javob."""
    now = time.monotonic()
    if force or now - _seen.get(user.id, 0) > SEEN_TTL:
        try:
            status, data = await api.seen(user, chat_id)
            if status == 200:
                _seen[user.id] = now
                _admin[user.id] = (bool(data.get("admin")), now)
        except SiteUnavailable as exc:
            logging.warning("Obunachini yozib bo'lmadi: %s", exc)
    return is_admin_cached(user.id)


def is_admin_cached(user_id: int) -> bool:
    if user_id in OWNERS:
        return True
    flag, at = _admin.get(user_id, (False, 0.0))
    return flag and time.monotonic() - at < ADMIN_TTL


async def is_admin(user: types.User, chat_id: int) -> bool:
    """/admin uchun: huquq saytda hozirgina berilgan/olingan bo'lsa ham to'g'ri javob."""
    return user.id in OWNERS or await touch(user, chat_id, force=True)


async def channels() -> List[dict]:
    global _channels
    items, at = _channels
    if time.monotonic() - at < CHANNELS_TTL:
        return items
    try:
        status, data = await api.channels()
        if status == 200:
            _channels = (data.get("channels", []), time.monotonic())
    except SiteUnavailable as exc:
        logging.warning("Kanallar ro'yxatini olib bo'lmadi: %s", exc)
    return _channels[0]


def reset_channels() -> None:
    """Kanal qo'shilganda/o'chirilganda: ro'yxat ham, "obuna bo'lgan" natijalar ham yangidan tekshiriladi."""
    global _channels
    _channels = ([], 0.0)
    _member_ok.clear()


async def _is_member(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except TelegramAPIError as exc:
        # bot kanaldan chiqarilgan yoki kanal o'chirilgan — foydalanuvchini shu sabab bilan qulflab qo'ymaymiz
        logging.warning("Kanal %s a'zoligini tekshirib bo'lmadi: %s", chat_id, exc)
        return True
    if member.status == types.ChatMemberStatus.RESTRICTED:
        return bool(getattr(member, "is_member", False))
    return member.status not in (types.ChatMemberStatus.LEFT, types.ChatMemberStatus.KICKED)


async def missing_channels(bot: Bot, user_id: int) -> List[dict]:
    items = await channels()
    if not items:
        return []
    now = time.monotonic()
    if _member_ok.get(user_id, 0) > now:
        return []
    results = await asyncio.gather(*(_is_member(bot, ch["chat_id"], user_id) for ch in items))
    missing = [ch for ch, ok in zip(items, results) if not ok]
    if not missing:
        _member_ok[user_id] = now + MEMBER_OK_TTL
    return missing
