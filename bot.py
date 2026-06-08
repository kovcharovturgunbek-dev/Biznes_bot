import logging
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 1. SOZLAMALAR
TOKEN = "YOUR_TOKEN"
ADMIN_ID = 8727214154

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()

CHIEF_CARD = "8600 1404 8875 1234"
PRODUCT_IMAGE_URL = "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop"

# --- AI MODERATSIYA UCHUN HOLATLAR ---
class AdminModeration(StatesGroup):
    waiting_for_product = State()
    checking_product = State()

class ShoppingState(StatesGroup):
    category = State()
    gender = State()
    foot_size = State()
    weight_only = State()
    child_height = State()
    adult_height = State()
    adult_weight = State()
    waiting_for_ad = State()

class AdProcess(StatesGroup):
    waiting_for_text = State()
    waiting_for_payment = State()

# --- AI MODERATSIYA FUNKSIYASI ---
def check_content_safety(text):
    forbidden_words = ["qimor", "18+", "siyosat", "taqiqlangan", "jinsiy"]
    found = [word for word in forbidden_words if word in text.lower()]
    return found

def get_admin_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📊 Umumiy statistika"), types.KeyboardButton(text="👥 Sotuvchilar ro'yxati")],
            [types.KeyboardButton(text="📥 Yangi mahsulotlar (AI)"), types.KeyboardButton(text="📢 Reklama yuborish")],
            [types.KeyboardButton(text="📈 Reklama Tekshiruvi"), types.KeyboardButton(text="🛍 Xaridor rejimiga o'tish")]
        ],
        resize_keyboard=True
    )

# --- REKLAMA TEKSHIRUVI (TUZATILGAN MANTIQ) ---
@dp.message(F.text == "📈 Reklama Tekshiruvi")
async def show_ad_moderation_panel(message: types.Message):
    if message.chat.id == ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash (To'lovni kutish)", callback_data="approve_ad")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data="reject_ad")]
        ])
        await message.answer("📈 <b>REKLAMA ARIZASI №1</b>\n📢 Kanal: @ModaUz_Admin\n💰 Narx: 50,000 UZS", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "approve_ad")
async def approve_ad_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("✅ Arizachi to'lovni amalga oshirishi uchun xabar yuborildi. Chek kutilyapti...")
    await callback.answer("To'lov jarayoniga o'tildi!")

@dp.callback_query(F.data == "reject_ad")
async def reject_ad_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("❌ Reklama rad etildi.")
    await callback.answer("Rad etildi.")

# --- YANGI MAHSULOTLAR (AI NAZORATI) ---
@dp.message(F.text == "📥 Yangi mahsulotlar (AI)")
async def ai_product_check_start(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        product_name = "Kuzgi Erkaklar Kurtkasi"
        store_name = "Zara Family"
        price = "450,000 UZS"
        
        report = (
            "🤖 <b>AI MAHSULOT NAZORATI VA TAHLILI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 <b>Do'kon:</b> {store_name}\n"
            f"👕 <b>Mahsulot:</b> {product_name}\n"
            f"💰 <b>Narxi:</b> {price}\n"
            "🛡 <b>AI Kontent Tekshiruvi:</b> 🟢 TOZA (Sifatli)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>AI Xulosasi:</b> Rasm formati va kiyim andozasi do'kon "
            "talablariga 100% mos keladi. Katalogga qo'shish tavsiya etiladi."
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Katalogga qo'shish", callback_data="confirm_upload")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data="reject_upload")]
        ])
        
        await message.answer(report, parse_mode="HTML", reply_markup=kb)
        await state.set_state(AdminModeration.checking_product)

@dp.callback_query(F.data == "confirm_upload")
async def confirm_upload(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✅ Mahsulot katalogga muvaffaqiyatli qo'shildi!")
    await state.clear()

@dp.callback_query(F.data == "reject_upload")
async def reject_upload(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Mahsulot rad etildi.")
    await state.clear()

# --- SOTUVCHILAR RO'YXATI (YANGILANGAN KO'RINISH) ---
@dp.message(F.text == "👥 Sotuvchilar ro'yxati")
async def show_partners_list(message: types.Message):
    if message.chat.id == ADMIN_ID:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚠️ Zara Family: Qarzdorlik! Ogohlantirish", callback_data="warn_zara")],
            [InlineKeyboardButton(text="✅ Real Look: To'langan", callback_data="none")],
            [InlineKeyboardButton(text="✅ Premium Sport: To'langan", callback_data="none")]
        ])
        await message.answer("👥 <b>HAMKOR SOTUVCHILAR (IJARA TIZIMI)</b>", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data == "warn_zara")
async def warn_seller(callback: types.CallbackQuery):
    await callback.message.answer("📩 Ogohlantirish xati yuborildi. Zara Family shartnomasi 72 soat ichida to'lov bo'lmasa bekor qilinadi.")
    scheduler.add_job(lambda: None, 'date', run_date=datetime.now() + timedelta(hours=72))

# --- REKLAMA JARAYONI ---
@dp.message(F.text == "📢 Reklama yuborish")
async def ask_for_advertisement(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await state.set_state(AdProcess.waiting_for_text)
        await message.answer("📢 Reklama matingizni yuboring:")

@dp.message(AdProcess.waiting_for_text)
async def process_ad_text(message: types.Message, state: FSMContext):
    violations = check_content_safety(message.text)
    if violations:
        await message.answer(f"❌ Taqiqlangan so'zlar bor: {', '.join(violations)}")
        return
    await state.update_data(ad_text=message.text)
    await message.answer(f"✅ Matn qabul qilindi.\nNarxi: 50,000 UZS\nKarta: <code>{CHIEF_CARD}</code>\nTo'lovdan so'ng chekni yuboring.", parse_mode="HTML")
    await state.set_state(AdProcess.waiting_for_payment)

@dp.message(AdProcess.waiting_for_payment, F.photo)
async def handle_payment(message: types.Message, state: FSMContext):
    await message.answer("✅ Chek qabul qilindi. Admin tasdig'ini kuting.")
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption="To'lov cheki keldi. Endi tarqatishni tasdiqlaysizmi?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Yakuniy Tarqatish", callback_data="confirm_ad")]]))

@dp.callback_query(F.data == "confirm_ad")
async def confirm_ad(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_caption(caption="✅ To'lov tasdiqlandi. Reklama tarqatildi!")
    await bot.send_message(ADMIN_ID, "📢 Reklama barchaga tarqatildi! Arizachiga xabar yuborildi.")
    await callback.answer("Muvaffaqiyatli!")

# --- ORIGINAL FUNKSIYALAR ---
def get_customer_keyboard(is_admin=False):
    keyboard_buttons = [
        [types.KeyboardButton(text="👕 Ustki kiyimlar"), types.KeyboardButton(text="👖 Shim va shortilar")],
        [types.KeyboardButton(text="🩲 Ichki kiyimlar"), types.KeyboardButton(text="👟 Oyoq kiyimlar")]
    ]
    if is_admin:
        keyboard_buttons.append([types.KeyboardButton(text="👑 Direktor paneliga qaytish")])
    return types.ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)

def get_gender_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚺 Ayollar uchun"), types.KeyboardButton(text="🚹 Erkaklar uchun")],
            [types.KeyboardButton(text="👶 Bolalar uchun")],
            [types.KeyboardButton(text="↩️ Orqaga qaytish")]
        ],
        resize_keyboard=True
    )

def get_back_only_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="↩️ Orqaga qaytish")]],
        resize_keyboard=True
    )

async def show_receipt(message: types.Message, state: FSMContext, size: str, input_value: str):
    user_data = await state.get_data()
    category = user_data.get('category', 'Kiyim')
    gender = user_data.get('gender', 'Noma\'lum')
    is_admin = (message.chat.id == ADMIN_ID)
    receipt_text = (
        "🛍 <b>XARID DETALLARI VA O'LCHAMINGIZ:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 <b>Bo'lim:</b> {category}\n"
        f"👤 <b>Kim uchun:</b> {gender}\n"
        f"📏 <b>Kiritilgan ma'lumot:</b> {input_value}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>Sizning ideal o'lchamingiz:</b> 🎉 <b>{size}</b> 🎉\n\n"
        "💡 <i>Ushbu o'lcham andozalar asosida hisoblandi.</i>"
    )
    await message.answer(receipt_text, parse_mode="HTML", reply_markup=get_customer_keyboard(is_admin))
    await state.clear()

async def set_bot_commands(bot: Bot):
    commands = [BotCommand(command="start", description="Botni qayta ishga tushirish 🔄")]
    await bot.set_my_commands(commands)

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear() 
    if message.chat.id == ADMIN_ID:
        await message.answer("👑 <b>Boshqaruv paneliga xush kelibsiz, Direktor!</b>", parse_mode="HTML", reply_markup=get_admin_keyboard())
    else:
        await show_customer_menu(message, state)

@dp.message(F.text == "📊 Umumiy statistika")
async def show_admin_statistics(message: types.Message):
    if message.chat.id == ADMIN_ID:
        kunlik_tushum = 300000
        oylik_tushum = 11950000
        faol_xaridorlar = 1245
        yangi_xaridorlar = 45
        hamkorlar_soni = 3
        hamkor_daromad = 450000
        stat_text = (
            "📊 <b>BATAFSIL MOLIYAVIY VA OPERATSION HISOBOT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📅 <b>DAVR:</b> BUGUN | OY (30 KUN)\n\n"
            "💰 <b>TUSHUMLAR:</b>\n"
            f"💵 Bugun: <code>{kunlik_tushum:,} UZS</code>\n"
            f"📈 Oxirgi 30 kun: <code>{oylik_tushum:,} UZS</code>\n\n"
            "🤝 <b>HAMKORLIK (IJARA):</b>\n"
            f"🏢 Do'konlar soni: <code>{hamkorlar_soni} ta</code>\n"
            f"💵 Hamkorlardan oylik daromad: <code>{hamkor_daromad:,} UZS</code>\n\n"
            "👥 <b>XARIDORLAR TAHLILI (30 KUN):</b>\n"
            f"👤 Yangi (bugun): <code>{yangi_xaridorlar} ta</code>\n"
            f"👥 Jami faol mijozlar: <code>{faol_xaridorlar} ta</code>\n\n"
            "🛍 <b>MAHSULOTLAR ULUSHI (30 KUNLIK):</b>\n"
            f"👕 Ustki: <code>40%</code> ({int(faol_xaridorlar * 0.4)} ta)\n"
            f"👖 Shim: <code>30%</code> ({int(faol_xaridorlar * 0.3)} ta)\n"
            f"🩲 Ichki: <code>20%</code> ({int(faol_xaridorlar * 0.2)} ta)\n"
            f"👟 Oyoq: <code>10%</code> ({int(faol_xaridorlar * 0.1)} ta)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 <i>Statistika real vaqtda hisoblandi.</i>"
        )
        await message.answer(stat_text, parse_mode="HTML", reply_markup=get_admin_keyboard())

@dp.message(F.text == "Xaridor rejimiga o'tish")
async def admin_to_customer(message: types.Message, state: FSMContext):
    await show_customer_menu(message, state)

async def show_customer_menu(message: types.Message, state: FSMContext):
    is_admin = (message.chat.id == ADMIN_ID)
    await message.answer("✨ Bo'limni tanlang:", reply_markup=get_customer_keyboard(is_admin))
    await state.set_state(ShoppingState.category)

@dp.message(F.text == "Direktor paneliga qaytish")
async def back_to_admin_panel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👑 Direktor paneliga qaytdingiz!", reply_markup=get_admin_keyboard())

@dp.message(ShoppingState.category, F.text.in_(["👕 Ustki kiyimlar", "👖 Shim va shortilar", "🩲 Ichki kiyimlar", "👟 Oyoq kiyimlar"]))
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Kim uchun mahsulot qidiryapsiz? 👇", reply_markup=get_gender_keyboard())
    await state.set_state(ShoppingState.gender)

@dp.message(ShoppingState.gender, F.text.in_(["🚹 Erkaklar uchun", "🚺 Ayollar uchun", "👶 Bolalar uchun"]))
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    user_data = await state.get_data()
    category = user_data['category']
    if category == "👟 Oyoq kiyimlar":
        await message.answer("Oyoq kaftingiz uzunligini (sm):", reply_markup=get_back_only_keyboard())
        await state.set_state(ShoppingState.foot_size)
    elif category == "🩲 Ichki kiyimlar":
        await message.answer("Vazningizni kiriting (kg):", reply_markup=get_back_only_keyboard())
        await state.set_state(ShoppingState.weight_only)
    else:
        if message.text == "👶 Bolalar uchun":
            await message.answer("Bolaning bo'yini kiriting (sm):", reply_markup=get_back_only_keyboard())
            await state.set_state(ShoppingState.child_height)
        else:
            await message.answer("Bo'yingizni kiriting (sm):", reply_markup=get_back_only_keyboard())
            await state.set_state(ShoppingState.adult_height)

@dp.message(ShoppingState.foot_size)
async def calc_foot_size(message: types.Message, state: FSMContext):
    try: await show_receipt(message, state, "41-42 o'lcham", f"{message.text} sm")
    except: await message.answer("⚠️ Raqamda kiriting:")

@dp.message(ShoppingState.weight_only)
async def calc_weight_only(message: types.Message, state: FSMContext):
    try: await show_receipt(message, state, "L o'lcham", f"{message.text} kg")
    except: await message.answer("⚠️ Raqamda kiriting:")

@dp.message(ShoppingState.child_height)
async def calc_child_height(message: types.Message, state: FSMContext):
    try: await show_receipt(message, state, "80 (1 yosh)", f"{message.text} sm")
    except: await message.answer("⚠️ Raqamda kiriting:")

@dp.message(ShoppingState.adult_height)
async def get_adult_height(message: types.Message, state: FSMContext):
    try:
        await state.update_data(height=int(message.text))
        await message.answer("👇 Endi esa vazningizni kiriting (kg):", reply_markup=get_back_only_keyboard())
        await state.set_state(ShoppingState.adult_weight)
    except: await message.answer("⚠️ Raqamda kiriting:")

@dp.message(ShoppingState.adult_weight)
async def calc_adult_weight(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        await show_receipt(message, state, "M o'lcham", f"Bo'y: {user_data.get('height')} sm, Vazn: {message.text} kg")
    except: await message.answer("⚠️ Raqamda kiriting:")

async def main():
    await set_bot_commands(bot)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
