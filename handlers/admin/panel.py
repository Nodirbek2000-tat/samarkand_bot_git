"""
/admin — faqat saytda Administrator huquqi berilgan akkauntlar (va .env dagi ADMINS) uchun.

📊 Statistika · 📢 Majburiy kanallar (qo'shish/o'chirish) · 📣 Reklama yuborish (istalgan xabar hammaga).
"""
import logging
import re
from html import escape

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest, ChatNotFound, MessageNotModified, TelegramAPIError

from keyboards.default import main_keyboard
from keyboards.inline import admin as kb
from loader import dp
from states.admin import AdminForm
from utils import audience
from utils.site_api import api

PANEL = "🛠 <b>Admin panel</b>\n\nKerakli bo'limni tanlang:"
NOT_ADMIN = "Bu bo'lim faqat administratorlar uchun."
CHANNEL_HELP = (
    "➕ <b>Kanal qo'shish</b>\n\n"
    "1. Avval botni o'sha kanalga <b>admin</b> qilib qo'ying.\n"
    "2. Keyin kanaldan istalgan postni shu yerga <b>forward</b> qiling yoki <code>@kanal_nomi</code> deb yozing.\n\n"
    "Bekor qilish — /bekor"
)
AD_HELP = (
    "📣 <b>Reklama yuborish</b>\n\n"
    "Reklama xabarini yuboring — matn, rasm, video, fayl yoki ovozli xabar. "
    "Obunachilarga aynan shu ko'rinishda boradi.\n\n"
    "Bekor qilish — /bekor"
)


def n(value) -> str:
    return f"{int(value or 0):,}".replace(",", " ")


async def show(target: types.Message, text: str, markup: types.InlineKeyboardMarkup, edit: bool):
    """Tugmadan kelganda — o'sha xabarni almashtiramiz (chat to'lib ketmaydi), aks holda yangi xabar."""
    if edit:
        try:
            await target.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
            return
        except MessageNotModified:
            return
        except BadRequest:
            pass  # eski xabarni tahrirlab bo'lmaydi (masalan, media) — yangisini yuboramiz
    await target.answer(text, reply_markup=markup, disable_web_page_preview=True)


async def guard(call: types.CallbackQuery) -> bool:
    if audience.is_admin_cached(call.from_user.id) or await audience.is_admin(call.from_user, call.message.chat.id):
        return True
    await call.answer(NOT_ADMIN, show_alert=True)
    return False


# ------------------------------------------------------------------------------------------- kirish


@dp.message_handler(commands=["admin"], state="*", chat_type=types.ChatType.PRIVATE)
async def admin_command(message: types.Message, state: FSMContext):
    if not await audience.is_admin(message.from_user, message.chat.id):
        await message.answer(NOT_ADMIN, reply_markup=main_keyboard)
        return
    await state.finish()
    await message.answer(PANEL, reply_markup=kb.panel_keyboard())


@dp.message_handler(commands=["bekor"], state=AdminForm.all_states, chat_type=types.ChatType.PRIVATE)
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Bekor qilindi.\n\n" + PANEL, reply_markup=kb.panel_keyboard())


@dp.callback_query_handler(text=kb.HOME, state="*")
async def home(call: types.CallbackQuery, state: FSMContext):
    if not await guard(call):
        return
    await state.finish()
    await show(call.message, PANEL, kb.panel_keyboard(), edit=True)
    await call.answer()


# ------------------------------------------------------------------------------------------- statistika


@dp.callback_query_handler(text=kb.STATS, state="*")
async def stats(call: types.CallbackQuery):
    if not await guard(call):
        return
    status, d = await api.stats()
    if status != 200:
        await call.answer("Sayt javob bermadi, keyinroq urinib ko'ring", show_alert=True)
        return
    s, site = d["subscribers"], d["site"]
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Bot obunachilari: <b>{n(s['total'])}</b>\n"
        f"   ✅ Faol: {n(s['active'])}\n"
        f"   🆕 Bugun: {n(s['today'])} · 7 kunda: {n(s['week'])}\n"
        f"   🚫 Botni bloklagan: {n(s['blocked'])}\n\n"
        "🌐 <b>Sayt</b>\n"
        f"   👤 Foydalanuvchilar: {n(site['users'])}\n"
        f"   📱 Bot orqali ro'yxatdan o'tgan: {n(site['registered'])}\n"
        f"   🛠 Xodimlar: {n(site['staff'])}\n\n"
        f"📢 Majburiy kanallar: {n(d['channels'])}\n"
        f"📨 Navbatdagi yuborishlar: {n(d['queue'])}"
    )
    last = d.get("last")
    if last:
        text += f"\n🕘 Oxirgisi: «{escape(last['title'] or 'Reklama')}» — {n(last['sent'])}/{n(last['total'])}"
    await show(call.message, text, kb.back_keyboard(), edit=True)
    await call.answer()


# ------------------------------------------------------------------------------------------- majburiy kanallar


async def channels_text():
    status, data = await api.channels()
    items = data.get("channels", []) if status == 200 else []
    if not items:
        body = "Hozircha kanal yo'q.\n\nQo'shilgan kanallarga obuna bo'lmaguncha foydalanuvchilar botdan foydalana olmaydi."
    else:
        lines = []
        for i, ch in enumerate(items, 1):
            name = escape(ch.get("title") or ch.get("username") or str(ch["chat_id"]))
            link = ch.get("link")
            lines.append(f"{i}. <a href=\"{link}\">{name}</a>" if link else f"{i}. {name}")
        body = "\n".join(lines) + "\n\n❌ — kanalni ro'yxatdan olib tashlash."
    return f"📢 <b>Majburiy kanallar</b>\n\n{body}", kb.channels_keyboard(items)


@dp.callback_query_handler(text=kb.CHANNELS, state="*")
async def channels(call: types.CallbackQuery, state: FSMContext):
    if not await guard(call):
        return
    await state.finish()
    text, markup = await channels_text()
    await show(call.message, text, markup, edit=True)
    await call.answer()


@dp.callback_query_handler(text_startswith=kb.CHANNEL_DEL, state="*")
async def channel_delete(call: types.CallbackQuery):
    if not await guard(call):
        return
    chat_id = int(call.data[len(kb.CHANNEL_DEL):])
    await api.delete_channel(chat_id)
    audience.reset_channels()
    text, markup = await channels_text()
    await show(call.message, text, markup, edit=True)
    await call.answer("Kanal olib tashlandi")


@dp.callback_query_handler(text=kb.CHANNEL_ADD, state="*")
async def channel_add(call: types.CallbackQuery):
    if not await guard(call):
        return
    await AdminForm.channel.set()
    await show(call.message, CHANNEL_HELP, kb.back_keyboard(kb.CHANNELS), edit=True)
    await call.answer()


def channel_ref(message: types.Message):
    """Forward qilingan post, @kanal_nomi, t.me/kanal_nomi yoki -100... ID."""
    if message.forward_from_chat:
        return message.forward_from_chat.id
    text = (message.text or "").strip()
    m = re.search(r"(?:t\.me/|telegram\.me/|@)([A-Za-z0-9_]{4,})", text)
    if m:
        return "@" + m.group(1)
    if re.fullmatch(r"-?\d{5,}", text):
        return int(text)
    return None


@dp.message_handler(state=AdminForm.channel, chat_type=types.ChatType.PRIVATE, content_types=types.ContentTypes.ANY)
async def channel_received(message: types.Message, state: FSMContext):
    ref = channel_ref(message)
    if ref is None:
        await message.answer("Kanaldan istalgan postni <b>forward</b> qiling yoki <code>@kanal_nomi</code> yozing.\n\nBekor qilish — /bekor")
        return
    try:
        chat = await message.bot.get_chat(ref)
    except (ChatNotFound, BadRequest):
        await message.answer("❌ Kanal topilmadi. Nomi to'g'rimi va bot kanalga qo'shilganmi?\n\nBekor qilish — /bekor")
        return
    if chat.type not in (types.ChatType.CHANNEL, types.ChatType.SUPERGROUP):
        await message.answer("Bu kanal emas. Kanaldan post forward qiling yoki <code>@kanal_nomi</code> yozing.")
        return

    title = escape(chat.title or chat.username or str(chat.id))
    me = await message.bot.me
    try:
        member = await message.bot.get_chat_member(chat.id, me.id)
        is_admin = member.status in (types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.CREATOR)
    except TelegramAPIError:
        is_admin = False
    if not is_admin:
        await message.answer(
            f"⚠️ Bot «<b>{title}</b>» kanalida <b>admin emas</b>.\n\n"
            "Majburiy obunani tekshirish uchun botni kanalga admin qilib qo'ying, so'ng postni qayta yuboring.\n\n"
            "Bekor qilish — /bekor"
        )
        return

    link = f"https://t.me/{chat.username}" if chat.username else (chat.invite_link or "")
    if not link:
        try:
            link = await message.bot.export_chat_invite_link(chat.id)
        except TelegramAPIError as exc:
            logging.warning("Kanal taklif havolasini olib bo'lmadi: %s", exc)
    status, _ = await api.add_channel(chat.id, chat.title or "", chat.username or "", link)
    if status != 200:
        await message.answer("Sayt javob bermadi, keyinroq qayta urinib ko'ring.")
        return
    audience.reset_channels()
    await state.finish()
    text, markup = await channels_text()
    await message.answer(f"✅ «<b>{title}</b>» majburiy kanallarga qo'shildi.\n\n" + text, reply_markup=markup, disable_web_page_preview=True)


# ------------------------------------------------------------------------------------------- reklama


@dp.callback_query_handler(text=kb.AD, state="*")
async def ad_start(call: types.CallbackQuery):
    if not await guard(call):
        return
    await AdminForm.ad.set()
    await show(call.message, AD_HELP, kb.back_keyboard(), edit=True)
    await call.answer()


@dp.message_handler(state=AdminForm.ad, chat_type=types.ChatType.PRIVATE, content_types=types.ContentTypes.ANY)
async def ad_received(message: types.Message, state: FSMContext):
    title = (message.text or message.caption or "").strip().split("\n", 1)[0][:80]
    await state.update_data(message_id=message.message_id, title=title)
    await AdminForm.ad_confirm.set()
    status, d = await api.stats()
    count = n(d["subscribers"]["active"]) if status == 200 else "barcha"
    await message.reply(
        f"☝️ Shu xabar <b>{count}</b> ta obunachiga yuboriladi. Tasdiqlaysizmi?",
        reply_markup=kb.ad_confirm_keyboard(),
    )


@dp.callback_query_handler(text=kb.AD_CANCEL, state="*")
async def ad_cancel(call: types.CallbackQuery, state: FSMContext):
    if not await guard(call):
        return
    await state.finish()
    await show(call.message, "Reklama bekor qilindi.\n\n" + PANEL, kb.panel_keyboard(), edit=True)
    await call.answer()


@dp.callback_query_handler(text=kb.AD_SEND, state=AdminForm.ad_confirm)
async def ad_send(call: types.CallbackQuery, state: FSMContext):
    if not await guard(call):
        return
    data = await state.get_data()
    await state.finish()
    status, res = await api.create_ad(call.message.chat.id, data["message_id"], data.get("title", ""))
    if status != 200:
        await call.answer("Sayt javob bermadi, qayta urinib ko'ring", show_alert=True)
        return
    ahead = max(0, int(res.get("queued", 1)) - 1)
    queue = f"\nNavbatda oldinda {ahead} ta yuborish bor." if ahead else ""
    await show(
        call.message,
        f"⏳ Reklama yuborilmoqda.{queue}\nTugagach, shu yerga hisobot keladi.",
        kb.back_keyboard(),
        edit=True,
    )
    await call.answer("Yuborish boshlandi")


@dp.callback_query_handler(text=kb.AD_SEND, state="*")
async def ad_send_stale(call: types.CallbackQuery):
    await call.answer("Bu reklama allaqachon yuborilgan yoki bekor qilingan.", show_alert=True)
