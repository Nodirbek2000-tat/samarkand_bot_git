from aiogram import Dispatcher

from loader import dp
from .audience import AudienceMiddleware
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(AudienceMiddleware())  # obunachilar ro'yxati + majburiy obuna
