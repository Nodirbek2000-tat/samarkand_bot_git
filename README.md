# Yangi Samarqand — Telegram bot (aiogram 2.25.2)

Saytga ro‘yxatdan o‘tish va kirish kodlarini beradigan bot. Keyinchalik sayt yubormoqchi bo‘lgan
boshqa xabarlar (murojaatlarga javoblar, e’lonlar) ham shu bot orqali boradi.

## Qanday ishlaydi

1. Foydalanuvchi botda **«📱 Telefon raqamni yuborish»** tugmasini bosadi → bot saytga (`/api/bot/register`) yuboradi →
   sayt foydalanuvchini ro‘yxatdan o‘tkazadi va 6 xonali kod qaytaradi → bot kodni yuboradi.
2. Keyingi safar **«🔑 Yangi kod olish»** (yoki `/kod`) → `/api/bot/code`.
3. Har 3 soniyada bot saytdagi xabarlar navbatini (`/api/bot/outbox`) tekshiradi va yetkazadi.
   Bu so‘rov saytga «bot ishlayapti» degan signal ham — admin panel bosh sahifasida ko‘rinadi.

Bot faqat shaxsiy chatda ishlaydi; boshqa odamning kontaktini yuborib ro‘yxatdan o‘tib bo‘lmaydi.

## Sozlash (`.env`)

```
BOT_TOKEN=...            # @BotFather bergan token — hech kimga ko‘rsatmang
ADMINS=123456789         # bot ishga tushganda xabar oladigan Telegram ID lar (vergul bilan)
ip=localhost
API_URL=http://127.0.0.1:8000/api   # Django manzili
BOT_API_SECRET=...       # ../samarkand/.env dagi BOT_API_SECRET bilan AYNAN bir xil
SITE_URL=http://localhost:3000      # https bo‘lsa, kod xabariga sayt havolasi qo‘shiladi
```

## Ishga tushirish

Avval Django (`../samarkand`) ishlab turgan bo‘lsin, keyin:

```
venv\Scripts\activate
python app.py
```

Hech narsa qo‘shimcha o‘rnatilmaydi: aiogram, aiohttp va environs venv’da bor.

## Tuzilma

| Fayl | Nima qiladi |
|---|---|
| `app.py` | ishga tushirish: buyruqlar, navbat worker’i, adminlarga xabar |
| `data/config.py` | `.env` sozlamalari |
| `utils/site_api.py` | sayt (Django) ichki API klienti |
| `utils/outbox.py` | sayt navbatidagi xabarlarni yetkazish |
| `handlers/users/start.py` | `/start` — ro‘yxatdan o‘tgan bo‘lsa kod, bo‘lmasa raqam so‘raydi |
| `handlers/users/contact.py` | kontakt → ro‘yxatdan o‘tish + kod |
| `handlers/users/code.py` | «🔑 Yangi kod olish», `/kod` |
| `handlers/users/help.py` | «ℹ️ Yordam», `/help` |
| `handlers/users/chat_member.py` | foydalanuvchi botni bloklasa — saytga aytadi |
| `handlers/users/texts.py` | barcha matnlar bir joyda |
| `keyboards/default/main.py` | tugmalar |
