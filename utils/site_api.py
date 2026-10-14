"""
Sayt (Django) ichki API'si bilan aloqa: /api/bot/*

Har bir so'rov `X-Bot-Secret` sarlavhasi bilan yuboriladi. Javob — (status, data) juftligi,
handlerlar status bo'yicha qaror qiladi. Sayt umuman javob bermasa — SiteUnavailable.
"""
import asyncio
import logging
from typing import Optional, Tuple

import aiohttp
from aiogram import types

from data import config


class SiteUnavailable(Exception):
    """Django ishlamayapti yoki tarmoq xatosi."""


class SiteAPI:
    def __init__(self, base_url: str, secret: str):
        self.base_url = base_url
        self.secret = secret
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"X-Bot-Secret": self.secret, "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15),
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(self, method: str, path: str, json: dict = None, params: dict = None) -> Tuple[int, dict]:
        url = f"{self.base_url}/{path}"
        try:
            async with self.session.request(method, url, json=json, params=params) as resp:
                try:
                    data = await resp.json(content_type=None)
                except ValueError:
                    data = {}
                if resp.status == 403 and (data or {}).get("detail") != "blocked":
                    logging.error("Sayt botni rad etdi (403). BOT_API_SECRET ikkala .env da bir xilmi? %s", data)
                return resp.status, data or {}
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise SiteUnavailable(f"{url}: {exc}") from exc

    # ------------------------------------------------------------------ yuqori darajadagi chaqiruvlar

    async def hello(self, me: types.User):
        return await self.request("POST", "bot/hello", {"username": me.username or "", "first_name": me.first_name or ""})

    async def register(self, user: types.User, contact: types.Contact, chat_id: int):
        return await self.request(
            "POST",
            "bot/register",
            {
                "telegram_id": user.id,
                "chat_id": chat_id,
                "phone": contact.phone_number,
                # kontaktdagi ism-familiya — odatda to'liqroq
                "first_name": contact.first_name or user.first_name or "",
                "last_name": contact.last_name or user.last_name or "",
                "username": user.username or "",
            },
        )

    async def code(self, user: types.User, chat_id: int):
        return await self.request(
            "POST", "bot/code", {"telegram_id": user.id, "chat_id": chat_id, "username": user.username or ""}
        )

    async def member(self, telegram_id: int, blocked: bool):
        return await self.request("POST", "bot/member", {"telegram_id": telegram_id, "blocked": blocked})

    async def outbox(self, limit: int = 30):
        return await self.request("GET", "bot/outbox", params={"limit": limit})

    async def ack(self, message_id: int, ok: bool, error: str = "", blocked: bool = False):
        return await self.request(
            "POST", f"bot/outbox/{message_id}/ack", {"ok": ok, "error": error[:255], "blocked": blocked}
        )


api = SiteAPI(config.API_URL, config.API_SECRET)
