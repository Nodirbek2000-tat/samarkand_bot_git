from aiogram import types

from loader import dp
from utils.site_api import api


@dp.my_chat_member_handler(chat_type=types.ChatType.PRIVATE)
async def bot_member(update: types.ChatMemberUpdated):
    # foydalanuvchi botni bloklasa — sayt unga xabar navbatga qo'ymaydi; qayta /start bosganda tiklanadi
    status = update.new_chat_member.status
    await api.member(update.from_user.id, blocked=status == types.ChatMemberStatus.KICKED)
