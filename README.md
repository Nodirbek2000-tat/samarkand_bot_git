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

## Admin panel (`/admin`) va hammaga yuborish

`/admin` faqat saytda **Administrator** huquqi berilgan akkauntlarda (bot orqali ro‘yxatdan o‘tgan bo‘lishi kerak)
va `.env` dagi `ADMINS` ID larida ishlaydi:

* **📊 Statistika** — bot obunachilari (jami, faol, bugun, bloklagan), sayt foydalanuvchilari, kanallar, navbat.
* **📢 Majburiy kanallar** — kanal qo‘shish: botni kanalga admin qiling → kanal postini forward qiling yoki `@kanal_nomi`
  yozing. Bot admin emasligini darhol aytadi. Qo‘shilgan kanallarga obuna bo‘lmaguncha foydalanuvchi botdan foydalana
  olmaydi («✅ Obuna bo‘ldim» tugmasi qayta tekshiradi). Adminlar tekshiruvdan ozod.
* **📣 Reklama yuborish** — istalgan xabar (matn, rasm, video, fayl...) tasdiqlangach barcha obunachilarga nusxalanadi;
  tugagach hisobot keladi.

Saytdagi yangi materiallar (yangilik, e’lon, loyiha/startap, film, fotohisobot, forum) — sayt admin panelidagi
**Telegram bot** bo‘limida «Saytdagi yangiliklarni botga yuborish» yoqilgan bo‘lsa, rasmi, qisqa matni va
«Davomini o‘qish» tugmasi bilan avtomatik yuboriladi (tugma faqat `SITE_URL` https bo‘lganda chiqadi).

Yuborish tezligi — Telegram limiti ichida eng yuqori (~25 xabar/soniya); rasm bir marta yuklanadi va qayta
ishlatiladi; bot qayta ishga tushsa, to‘xtagan joyidan davom etadi. Admin panelda yuborishni to‘xtatish mumkin.

## Sozlash (`.env`)

```
BOT_TOKEN=...            # @BotFather bergan token — hech kimga ko‘rsatmang
ADMINS=123456789         # Telegram ID lar (vergul bilan): ishga tushganda xabar oladi va /admin dan foydalana oladi
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
| `utils/broadcaster.py` | hammaga yuborish (saytdagi yangiliklar va reklama) |
| `utils/audience.py` | obunachilar, adminlar, majburiy kanallar keshi |
| `middlewares/audience.py` | har xabarda obunachini yozish va majburiy obunani tekshirish |
| `handlers/admin/panel.py` | `/admin`: statistika, majburiy kanallar, reklama |
| `handlers/users/subscription.py` | «✅ Obuna bo‘ldim» tugmasi |
| `handlers/users/start.py` | `/start` — ro‘yxatdan o‘tgan bo‘lsa kod, bo‘lmasa raqam so‘raydi |
| `handlers/users/contact.py` | kontakt → ro‘yxatdan o‘tish + kod |
| `handlers/users/code.py` | «🔑 Yangi kod olish», `/kod` |
| `handlers/users/help.py` | «ℹ️ Yordam», `/help` |
| `handlers/users/chat_member.py` | foydalanuvchi botni bloklasa — saytga aytadi |
| `handlers/users/texts.py` | barcha matnlar bir joyda |
| `keyboards/default/main.py` | tugmalar |
