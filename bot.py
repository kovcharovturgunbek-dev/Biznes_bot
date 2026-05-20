import asyncio
import logging
import os  # <-- .env ichidagi o'zgaruvchilarni o'qish uchun kutubxona
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# 1. Bot sozlamalarini xavfsiz o'qish
# Tizimda BOT_TOKEN bo'lsa uni oladi, aks holda default (orqadagi) tokenni ishlatadi
TOKEN = os.getenv("BOT_TOKEN", "8521448875:AAFJGG3HNOjPvGapB1BGmc2f0euXYKi32s8")
ADMIN_ID = int(os.getenv("ADMIN_ID", 8727214154))

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratish
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Bot holatlarini boshqarish (FSM)
class ShoppingState(StatesGroup):
    category = State()
    gender = State()
    foot_size = State()
    weight_only = State()
    child_height = State()
    adult_height = State()
    adult_weight = State()

# 👑 ADMIN TUGMALARI FUNCTION
def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📊 Umumiy statistika"), types.KeyboardButton(text="👥 Sotuvchilar ro'yxati")],
            [types.KeyboardButton(text="📢 Reklama yuborish"), types.KeyboardButton(text="🛍 Xaridor rejimiga o'tish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return markup

# 👤 JINSNI TANLASH TUGMALARI
def get_gender_keyboard():
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚹 Erkaklar uchun"), types.KeyboardButton(text="🚺 Ayollar uchun")],
            [types.KeyboardButton(text="👶 Bolalar uchun")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return markup


# ----------------- START BUYRUG'I (ADMIN YOKI MIJOZ) -----------------
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear() 
    chat_id = message.chat.id
    
    if chat_id == ADMIN_ID:
        admin_matn = (
            "👑 **Xush kelibsiz, Hurmatli Direktor!**\n\n"
            "Siz platformaning bosh boshqaruv paneliga kirdingiz.\n"
            "Quyidagi tugmalar orqali savdo markazini nazorat qilishingiz mumkin:"
        )
        await message.answer(admin_matn, parse_mode="Markdown", reply_markup=get_admin_keyboard())
    else:
        await show_customer_menu(message, state)


# Admin xaridor rejimiga o'tishini boshqarish
@dp.message(F.text == "🛍 Xaridor rejimiga o'tish")
async def admin_to_customer(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await show_customer_menu(message, state)


# Xaridor bosh menyusini ko'rsatish (Admin uchun qaytish tugmasi bilan)
async def show_customer_menu(message: types.Message, state: FSMContext):
    # Asosiy xaridor tugmalari
    keyboard_buttons = [
        [types.KeyboardButton(text="👕 Ustki kiyimlar"), types.KeyboardButton(text="👖 Shim va shortilar")],
        [types.KeyboardButton(text="🩲 Ichki kiyimlar"), types.KeyboardButton(text="👟 Oyoq kiyimlar")]
    ]
    
    # 👑 AGAR KIRGAN ODAM ADMIN BO'LSA, UNGA DIREKTOR PANELIGA QAYTISH TUGMASINI QO'SHISH
    if message.chat.id == ADMIN_ID:
        keyboard_buttons.append([types.KeyboardButton(text="👑 Direktor paneliga qaytish")])
        
    markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    premium_matn = (
        "👋 **Salom, uslubingiz mukammal boʻlishini xohlaysizmi?**\n\n"
        "Siz kiyim-kechak, oyoq kiyim va ichki kiyimlarning eng zamonaviy onlayn platformasiga kirdingiz.\n\n"
        "📐 Bizning tizimimiz yordamida uydan chiqmasdan, oʻz parametrlaringizga (boʻy, vazn, oyoq sm) "
        "mos keluvchi kiyimlarni xatosiz tanlay olasiz. Biz sizga xuddi shaxsiy tikinggandek mos keladigan oʻlchamni taqdim etamiz.\n\n"
        "👇 **Sifatli xaridni hoziroq boshlang, bo'limni tanlang:**"
    )
    
    await message.answer(text=premium_matn, parse_mode="Markdown", reply_markup=markup)
    await state.set_state(ShoppingState.category)


# Adminga xaridor rejimidan direktor rejimiga qaytish imkonini beruvchi xandler
@dp.message(F.text == "👑 Direktor paneliga qaytish")
async def back_to_admin_panel(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await state.clear()  # Xaridor seansini butunlay tozalash
        
        admin_matn = (
            "👑 **Direktor paneliga qaytdingiz!**\n\n"
            "Platforma boshqaruv tugmalari qayta faollashdi. Tizimni boshqarishingiz mumkin:"
        )
        await message.answer(admin_matn, parse_mode="Markdown", reply_markup=get_admin_keyboard())


# ----------------- KATEGORIYANI QABUL QILISH -----------------
@dp.message(ShoppingState.category, F.text.in_(["👕 Ustki kiyimlar", "👖 Shim va shortilar", "🩲 Ichki kiyimlar", "👟 Oyoq kiyimlar"]))
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Katalogimizdan kim uchun mahsulot qidiryapsiz?", reply_markup=get_gender_keyboard())
    await state.set_state(ShoppingState.gender)

@dp.message(ShoppingState.category)
async def invalid_category(message: types.Message):
    await message.answer("Iltimos, menyudagi tugmalardan birini tanlang:")


# ----------------- JINSNI QABUL QILISH VA SAVOLLARGA AJRATISH -----------------
@dp.message(ShoppingState.gender, F.text.in_(["🚹 Erkaklar uchun", "🚺 Ayollar uchun", "👶 Bolalar uchun"]))
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    user_data = await state.get_data()
    category = user_data['category']
    gender = message.text
    
    markup = types.ReplyKeyboardRemove()
    
    if category == "👟 Oyoq kiyimlar":
        await message.answer("👟 **Oyoq kiyim bo'limi**\n\nIltimos, oyoq kaftingiz uzunligini santimetrda kiriting (masalan: 26.5):", reply_markup=markup)
        await state.set_state(ShoppingState.foot_size)
    elif category == "🩲 Ichki kiyimlar":
        await message.answer("🩲 **Ichki kiyimlar bo'limi**\n\nIltimos, hozirgi vazningizni kiriting (kg hisobida, masalan: 70):", reply_markup=markup)
        await state.set_state(ShoppingState.weight_only)
    else:
        if gender == "👶 Bolalar uchun":
            await message.answer("👶 **Bolalar kiyimi bo'limi**\n\nIltimos, bolaning bo'yini kiriting (sm hisobida, masalan: 95):", reply_markup=markup)
            await state.set_state(ShoppingState.child_height)
        else:
            katalog = "ustki kiyim" if category == "👕 Ustki kiyimlar" else "shim/shorti"
            await message.answer(f"Tanlagan {katalog}ingiz sizga ideal o'tirishi uchun parametrlaringizni aniqlaymiz.\n\n👇 **Iltimos, bo'yingizni kiriting (sm):**", reply_markup=markup)
            await state.set_state(ShoppingState.adult_height)

@dp.message(ShoppingState.gender)
async def invalid_gender(message: types.Message):
    await message.answer("Iltimos, jinsni tugmalar orqali tanlang:", reply_markup=get_gender_keyboard())


# ----------------- AQLLI PARAMETRLARNI QABUL QILISH VA JAVOBLAR -----------------

@dp.message(ShoppingState.foot_size)
async def calc_foot_size(message: types.Message, state: FSMContext):
    try:
        foot_sm = float(message.text)
        size = "40"
        if foot_sm < 23.0: size = "35-36"
        elif 23.0 <= foot_sm < 24.0: size = "37"
        elif 24.0 <= foot_sm < 25.0: size = "39"
        elif 25.0 <= foot_sm < 26.0: size = "40"
        elif 26.0 <= foot_sm < 27.0: size = "41-42"
        elif 27.0 <= foot_sm < 28.0: size = "43"
        else: size = "44-45"
        await show_receipt(message, state, f"{size} o'lcham", f"Oyoq kafti: {foot_sm} sm")
    except ValueError:
        await message.answer("Iltimos, o'lchamni raqamda kiriting (masalan: 26.5):")

@dp.message(ShoppingState.weight_only)
async def calc_weight_only(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        size = "M"
        if weight <= 55: size = "S"
        elif weight <= 68: size = "M"
        elif weight <= 80: size = "L"
        elif weight <= 92: size = "XL"
        else: size = "XXL"
        await show_receipt(message, state, size, f"Vazn: {weight} kg")
    except ValueError:
        await message.answer("Iltimos, vaznni faqat raqamda kiriting:")

@dp.message(ShoppingState.child_height)
async def calc_child_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        size = "92"
        if height <= 56: size = "56 (0-3 oy)"
        elif height <= 68: size = "68 (6-9 oy)"
        elif height <= 80: size = "80 (1 yosh)"
        elif height <= 98: size = "98 (3 yosh)"
        elif height <= 116: size = "116 (5-6 yosh)"
        else: size = "128 (7-8 yosh)"
        await show_receipt(message, state, size, f"Bolaning bo'yi: {height} sm")
    except ValueError:
        await message.answer("Iltimos, bo'yni butun raqamda kiriting:")

@dp.message(ShoppingState.adult_height)
async def get_adult_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        await state.update_data(height=height)
        await message.answer("👇 Vazningizni kiriting (kg):")
        await state.set_state(ShoppingState.adult_weight)
    except ValueError:
        await message.answer("Iltimos, bo'yingizni faqat raqamda kiriting:")

@dp.message(ShoppingState.adult_weight)
async def calc_adult_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        user_data = await state.get_data()
        height = user_data['height']
        gender = user_data['gender']
        category = user_data['category']
        
        size = "M"
        if weight <= 60: size = "S"
        elif 61 <= weight <= 73: size = "M"
        elif 74 <= weight <= 85: size = "L"
        elif 86 <= weight <= 95: size = "XL"
        else: size = "XXL"
            
        if category == "👖 Shim va shortilar" and gender == "🚹 Erkaklar uchun":
            if size == "S": size = "28-29"
            elif size == "M": size = "30-31"
            elif size == "L": size = "32-33"
            elif size == "XL": size = "34-36"
            else: size = "38+"

        await show_receipt(message, state, size, f"{height} sm / {weight} kg")
    except ValueError:
        await message.answer("Iltimos, vazningizni faqat raqamda kiriting:")


# YAKUNIY RECEPT (CHEK) CHIQARISH
async def show_receipt(message: types.Message, state: FSMContext, size, params):
    user_data = await state.get_data()
    category = user_data['category']
    gender = user_data['gender']
    
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Katalogni ko'rish 🛍"), types.KeyboardButton(text="Boshqatdan hisoblash 🔄")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    summary = (
        f"🛒 **Sizning aqlli tanlovingiz:**\n\n"
        f"🗂 Bo'lim: {category}\n"
        f"👤 Kim uchun: {gender}\n"
        f"📏 Kiritilgan parametr: {params}\n"
        f"✨ **Bot tavsiya qilgan ideal o'lcham: {size}**\n\n"
        f"Ushbu o'lchamdagi mahsulotlar katalogini ko'rishni istaysizmi?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=markup)
    await state.clear() 


# Botni ishga tushirish mantiqi
async def main():
    print("Chaqmoqdek tez ishlaydigan asinxron bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
