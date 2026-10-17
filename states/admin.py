from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminForm(StatesGroup):
    channel = State()  # kanaldan forward yoki @kanal_nomi kutilmoqda
    ad = State()  # reklama xabari kutilmoqda
    ad_confirm = State()  # reklamani tasdiqlash
