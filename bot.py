import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

# 1. Sozlamalar
TOKEN = os.getenv("BOT_TOKEN", "8521448875:AAFJGG3HNOjPvGapB1BGmc2f0euXYKi32s8")
ADMIN_ID = int(os.getenv("ADMIN_ID", 8727214154))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class ShoppingState(StatesGroup):
    category = State()
    gender = State()
    foot_size = State()
    weight_only = State()
    child_height = State()
    adult_height = State()
    adult_weight = State()

# 👑 ADMIN PANEL (REPLY)
def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📊 Umumiy statistika"), types.KeyboardButton(text="👥 Sotuvchilar ro'yxati")],
            [types.KeyboardButton(text="📢 Reklama yuborish"), types.KeyboardButton(text="🛍 Xaridor rejimiga o'tish")]
        ],
        resize_keyboard=True
    )
    return markup

# 🛍 BOSH MENYU (REPLY)
def get_customer_keyboard(is_admin=False):
    keyboard_buttons = [
        [types.KeyboardButton(text="👕 Ustki kiyimlar"), types.KeyboardButton(text="👖 Shim va shortilar")],
        [types.KeyboardButton(text="🩲 Ichki kiyimlar"), types.KeyboardButton(text="👟 Oyoq kiyimlar")]
    ]
    if is_admin:
        keyboard_buttons.append([types.KeyboardButton(text="👑 Direktor paneliga qaytish")])
        
    return types.ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)

# 👤 JINSNI TANLASH MENYUSI (REPLY)
def get_gender_keyboard():
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚺 Ayollar uchun"), types.KeyboardButton(text=" Erkaklar uchun")],
            [types.KeyboardButton(text="👶 Bolalar uchun")],
            [types.KeyboardButton(text="↩️ Orqaga orqaga qaytish")]
        ],
        resize_keyboard=True
    )
    return markup

# ↩️ FAQAT ORQAGA QAYTISH TUGMASI
def get_back_only_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="↩️ Orqaga orqaga qaytish")]],
        resize_keyboard=True
    )

# 🚀 1. BOTGA BUYRUQLARNI JOYLASH (MENU BUTTONS)
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni qayta ishga tushirish 🔄"),
        BotCommand(command="help", description="Yordam va qo'llanma ❓"),
    ]
    await bot.set_my_commands(commands)

# ----------------- HANDLERS -----------------

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear() 
    if message.chat.id == ADMIN_ID:
        admin_matn = (
            "👑 *Xush kelibsiz, Hurmatli Direktor!*\n\n"
            "Siz platformaning bosh boshqaruv paneliga kirdingiz.\n"
            "Quyidagi tugmalar orqali savdo markazini nazorat qiling:"
        )
        await message.answer(admin_matn, parse_mode="Markdown", reply_markup=get_admin_keyboard())
    else:
        await show_customer_menu(message, state)

# HELP BUYRUG'I
@dp.message(Command("help"))
async def help_handler(message: types.Message):
    help_text = (
        "❓ *Botdan qanday foydalaniladi?*\n\n"
        "1️⃣ Bosh menyudan o'zingizga kerakli kiyim bo'limini tanlang.\n"
        "2️⃣ Kim uchun xarid qilayotganingizni belgilang.\n"
        "3️⃣ Bo'y va vazningizni kiriting.\n\n"
        "✨ Tizim sizga eng ideal o'lchamni avtomat hisoblab beradi!"
    )
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(F.text == "🛍 Xaridor rejimiga o'tish")
async def admin_to_customer(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await show_customer_menu(message, state)

async def show_customer_menu(message: types.Message, state: FSMContext):
    is_admin = (message.chat.id == ADMIN_ID)
    premium_matn = (
        "✨ *Salom! Mukammal uslub olamiga xush kelibsiz!*\n\n"
        "👇 _Xaridni boshlash uchun quyidagi bo'limlardan birini tanlang:_"
    )
    await message.answer(text=premium_matn, parse_mode="Markdown", reply_markup=get_customer_keyboard(is_admin))
    await state.set_state(ShoppingState.category)

@dp.message(F.text == "👑 Direktor paneliga qaytish")
async def back_to_admin_panel(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await state.clear()
        await message.answer("👑 *Direktor paneliga qaytdingiz!*", parse_mode="Markdown", reply_markup=get_admin_keyboard())

@dp.message(F.text == "↩️ Orqaga orqaga qaytish")
async def global_back_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await show_customer_menu(message, state)

# KATEGORIYA QABUL QILISH
@dp.message(ShoppingState.category, F.text.in_(["👕 Ustki kiyimlar", "👖 Shim va shortilar", "🩲 Ichki kiyimlar", "👟 Oyoq kiyimlar"]))
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(
        f"Katalogimizdan kim uchun mahsulot qidiryapsiz? 👇", 
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ShoppingState.gender)

# JINSNI QABUL QILISH
@dp.message(ShoppingState.gender, F.text.in_([" Erkaklar uchun", "🚺 Ayollar uchun", "👶 Bolalar uchun"]))
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    user_data = await state.get_data()
    category = user_data['category']
    
    # Bu yerda raqam kiritish misollariga fon (inline code block) berildi: `26.5` kabi
    if category == "👟 Oyoq kiyimlar":
        await message.answer("👟 *Oyoq kiyim bo'limi*\n\nIltimos, oyoq kaftingiz uzunligini santimetrda kiriting (masalan: `26.5`):", parse_mode="Markdown", reply_markup=get_back_only_keyboard())
        await state.set_state(ShoppingState.foot_size)
    elif category == "🩲 Ichki kiyimlar":
        await message.answer("🩲 *Ichki kiyimlar bo'limi*\n\nIltimos, hozirgi vazningizni kiriting (kg hisobida, masalan: `70`):", parse_mode="Markdown", reply_markup=get_back_only_keyboard())
        await state.set_state(ShoppingState.weight_only)
    else:
        if message.text == "👶 Bolalar uchun":
            await message.answer("👶 *Bolalar kiyimi bo'limi*\n\nIltimos, bolaning bo'yini kiriting (sm hisobida, masalan: `95`):", parse_mode="Markdown", reply_markup=get_back_only_keyboard())
            await state.set_state(ShoppingState.child_height)
        else:
            katalog = "ustki kiyimingiz" if category == "👕 Ustki kiyimlar" else "shimingiz"
            await message.answer(f"Tanlagan {katalog} sizga ideal o'tirishi uchun:\n\n👇 *Bo'yingizni kiriting (sm):*", parse_mode="Markdown", reply_markup=get_back_only_keyboard())
            await state.set_state(ShoppingState.adult_height)

# PARAMETRLAR VA HISOB-KITOB
@dp.message(ShoppingState.foot_size)
async def calc_foot_size(message: types.Message, state: FSMContext):
    try:
        foot_sm = float(message.text)
        size = "40" if 25.0 <= foot_sm < 26.0 else "41-42" if 26.0 <= foot_sm < 27.0 else "39" if 24.0 <= foot_sm < 25.0 else "43" if 27.0 <= foot_sm < 28.0 else "37" if 23.0 <= foot_sm < 24.0 else "35-36" if foot_sm < 23.0 else "44-45"
        await show_receipt(message, state, f"{size} o'lcham", f"{foot_sm} sm")
    except ValueError:
        await message.answer("⚠️ Iltimos, o'lchamni raqamda kiriting:", reply_markup=get_back_only_keyboard())

@dp.message(ShoppingState.weight_only)
async def calc_weight_only(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        size = "S" if weight <= 55 else "M" if weight <= 68 else "L" if weight <= 80 else "XL" if weight <= 92 else "XXL"
        await show_receipt(message, state, size, f"{weight} kg")
    except ValueError:
        await message.answer("⚠️ Iltimos, vaznni faqat butun raqamda kiriting:", reply_markup=get_back_only_keyboard())

@dp.message(ShoppingState.child_height)
async def calc_child_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        size = "56 (0-3 oy)" if height <= 56 else "68 (6-9 oy)" if height <= 68 else "80 (1 yosh)" if height <= 80 else "98 (3 yosh)" if height <= 98 else "116 (5-6 yosh)" if height <= 116 else "128 (7-8 yosh)"
        await show_receipt(message, state, size, f"{height} sm")
    except ValueError:
        await message.answer("⚠️ Iltimos, bo'yni butun raqamda kiriting:", reply_markup=get_back_only_keyboard())

@dp.message(ShoppingState.adult_height)
async def get_adult_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        await state.update_data(height=height)
        await message.answer("👇 *Endi esa vazningizni kiriting (kg):*", parse_mode="Markdown", reply_markup=get_back_only_keyboard())
        await state.set_state(ShoppingState.adult_weight)
    except ValueError:
        await message.answer("⚠️ Iltimos, bo'yingizni faqat raqamda kiriting:", reply_markup=get_back_only_keyboard())

@dp.message(ShoppingState.adult_weight)
async def calc_adult_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        user_data = await state.get_data()
        height = user_data['height']
        gender = user_data['gender']
        category = user_data['category']
        
        size = "S" if weight <= 60 else "M" if 61 <= weight <= 73 else "L" if 74 <= weight <= 85 else "XL" if 86 <= weight <= 95 else "XXL"
        if category == "👖 Shim va shortilar" and gender == " Erkaklar uchun":
            size = "28-29" if size == "S" else "30-31" if size == "M" else "32-33" if size == "L" else "34-36" if size == "XL" else "38+"

        await show_receipt(message, state, size, f"{height} sm / {weight} kg")
    except ValueError:
        await message.answer("⚠️ Iltimos, vazningizni faqat raqamda kiriting:", reply_markup=get_back_only_keyboard())

# YAKUNIY CHEK
async def show_receipt(message: types.Message, state: FSMContext, size, params):
    user_data = await state.get_data()
    category = user_data['category']
    gender = user_data['gender']
    
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Katalogni ko'rish 🛍"), types.KeyboardButton(text="Boshqatdan hisoblash 🔄")]],
        resize_keyboard=True
    )
    
    # Natija qismidagi tavsiya etilgan o'lcham fon (kod ko'rinishi) ichiga olindi: `XXL` kabi
    summary = (
        f"📋 ━━━━ 🌟 *BUYURTMA CHEKI* 🌟 ━━━━\n\n"
        f"🗂 *Bo'lim:* {category}\n"
        f"👤 *Kim uchun:* {gender}\n"
        f"📏 *Kiritilgan parametr:* {params}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ *Tavsiya etilgan o'lcham:* `{size}`\n\n"
        f"Ushbu o'lchamdagi mahsulotlarni ko'rishni istaysizmi?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=markup)
    await state.clear()

@dp.message(F.text == "Boshqatdan hisoblash 🔄")
async def restart_calculation(message: types.Message, state: FSMContext):
    await show_customer_menu(message, state)

@dp.message()
async def invalid_message(message: types.Message):
    await message.answer("⚠️ Iltimos, menyudagi tugmalardan foydalaning.")

async def main():
    # Buyruqlarni ro'yxatdan o'tkazamiz
    await set_bot_commands(bot)
    print("Buyruqlar va matn dizaynlari muvaffaqiyatli yuklandi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
