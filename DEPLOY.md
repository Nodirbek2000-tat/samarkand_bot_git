# Telegram bot — serverga chiqarish

Tartib: **1. backend → 2. frontend → 3. bot**. Backend ishlab turgan bo‘lishi kerak
(bot unga umumiy `mentadbirkor` Docker tarmog‘i orqali ulanadi).

## 1. O‘rnatish

```bash
git clone https://github.com/Nodirbek2000-tat/samarkand_bot_git.git /opt/mentadbirkor/bot
cd /opt/mentadbirkor/bot
cp server.env.example .env
nano .env        # BOT_TOKEN, ADMINS, backend dagi bilan bir xil BOT_API_SECRET
docker compose up -d --build
```

> ⚠️ Bitta token bilan bot faqat **bitta joyda** ishlay oladi. Serverdagi bot ishga tushgach,
> kompyuterdagi `python app.py` ni to‘xtating (aks holda Telegram «Conflict» xatosini beradi).

## 2. Tekshirish va loglar

```bash
docker compose ps
docker compose logs -f bot
```

Saytdagi admin panel bosh sahifasida «Telegram bot — Ishlayapti» ko‘rinishi kerak.

## 3. Yangilash

```bash
cd /opt/mentadbirkor/bot
git pull
docker compose up -d --build
```
