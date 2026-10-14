from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_CONTACT = "📱 Telefon raqamni yuborish"
BTN_CODE = "🔑 Yangi kod olish"
BTN_HELP = "ℹ️ Yordam"

# ro'yxatdan o'tish: Telegram raqamni o'zi yuboradi (qo'lda yozish shart emas, raqam tasdiqlangan bo'ladi)
contact_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton(BTN_CONTACT, request_contact=True)
)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton(BTN_CODE), KeyboardButton(BTN_HELP))
