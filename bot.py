import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# 1. Sozlamalar
TOKEN = os.getenv("BOT_TOKEN", "8521448875:AAFJGG3HNOjPvGapB1BGmc2f0euXYKi32s8")
ADMIN_ID = int(os.getenv(import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

# 👑 ADMIN PANEL (REPLY TUGMALAR)
def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📊 Umumiy statistika"), types.KeyboardButton(text="👥 Sotuvchilar ro'yxati")],
            [types.KeyboardButton(text="📢 Reklama yuborish"), types.KeyboardButton(text="🛍 Xaridor rejimiga o'tish")]
        ],
        resize_keyboard=True
    )
    return markup

# 🛍 BOSH KATEGORIYALAR (INLINE)
def get_categories_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="👕 Ustki kiyimlar", callback_data="cat:ustki")
    builder.button(text="👖 Shim va shortilar", callback_data="cat:shim")
    builder.button(text="🩲 Ichki kiyimlar", callback_data="cat:ichki")
    builder.button(text="👟 Oyoq kiyimlar", callback_data="cat:oyoq")
    builder.adjust(2, 2)
    return builder.as_markup()

# 👤 JINSNI TANLASH MENYUSI (INLINE)
def get_gender_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚹 Erkaklar", callback_data="gender:erkak")
    builder.button(text="🚺 Ayollar", callback_data="gender:ayol")
    builder.button(text="👶 Bolalar", callback_data="gender:bola")
    builder.button(text="↩️ Orqaga", callback_data="back:to_categories") # Orqaga tugmasi
    builder.adjust(2, 1, 1)
    return builder.as_markup()

# ↩️ FAQAT ORQAGA TUGMASI (INLINE)
def get_only_back_inline(target_step):
    builder = InlineKeyboardBuilder()
    builder.button(text="↩️ Orqaga", callback_data=f"back:{target_step}")
    return builder.as_markup()

# ----------------- REJA VA HANDLERLAR -----------------

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear() 
    if message.chat.id == ADMIN_ID:
        admin_matn = (
            "👑 **Xush kelibsiz, Hurmatli Direktor!**\n\n"
            "Siz platformaning bosh boshqaruv paneliga kirdingiz.\n"
            "Quyidagi tugmalar orqali savdo markazini nazorat qiling:"
        )
        await message.answer(admin_matn, parse_mode="Markdown", reply_markup=get_admin_keyboard())
    else:
        await send_welcome_menu(message)

@dp.message(F.text == "🛍 Xaridor rejimiga o'tish")
async def admin_to_customer(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await state.clear()
        await send_welcome_menu(message)

async def send_welcome_menu(message: types.Message):
    premium_matn = (
        "✨ **Salom! Mukammal uslub olamiga xush kelibsiz!**\n\n"
        "📐 Tizimimiz sizning parametrlaringiz asosida "
        "aynan sizga shaxsiy tiktirilgandek mos keladigan o'lchamni aniqlab beradi.\n\n"
        "👇 **Xaridni boshlash uchun bo'limni tanlang:**"
    )
    await message.answer(text=premium_matn, parse_mode="Markdown", reply_markup=get_categories_inline())

# 1-BOSQICH: KATEGORIYA TANLANGANDA
@dp.callback_query(F.data.startswith("cat:"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    cat_map = {"cat:ustki": "👕 Ustki kiyimlar", "cat:shim": "👖 Shim va shortilar", "cat:ichki": "🩲 Ichki kiyimlar", "cat:oyoq": "👟 Oyoq kiyimlar"}
    chosen_cat = cat_map[callback.data]
    
    await state.update_data(category=chosen_cat)
    await state.set_state(ShoppingState.gender)
    
    await callback.message.edit_text(
        text=f"» **Tanlandi:** {chosen_cat}\n\n**Kim uchun mahsulot qidiryapsiz?** 👇",
        parse_mode="Markdown",
        reply_markup=get_gender_inline()
    )

# ↩️ JINSDAN KATEGORIYAGA ORQAGA QAYTISH
@dp.callback_query(ShoppingState.gender, F.data == "back:to_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    premium_matn = (
        "✨ **Mukammal uslub olami**\n\n"
        "👇 **Iltimos, qaytadan o'zingizga kerakli bo'limni tanlang:**"
    )
    await callback.message.edit_text(text=premium_matn, parse_mode="Markdown", reply_markup=get_categories_inline())

# 2-BOSQICH: JINS TANLANGANDA PARAMETR SO'RASH
@dp.callback_query(ShoppingState.gender, F.data.startswith("gender:"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender_map = {"erkak": "🚹 Erkaklar", "ayol": "🚺 Ayollar", "bola": "👶 Bolalar"}
    chosen_gender = gender_map[callback.data.split(":")[1]]
    
    await state.update_data(gender=chosen_gender)
    user_data = await state.get_data()
    category = user_data['category']
    
    if category == "👟 Oyoq kiyimlar":
        await state.set_state(ShoppingState.foot_size)
        await callback.message.edit_text(
            "👟 **Oyoq kiyim bo'limi**\n\nIltimos, oyoq kaftingiz uzunligini santimetrda kiriting (masalan: `26.5`):", 
            parse_mode="Markdown", reply_markup=get_only_back_inline("to_gender")
        )
    elif category == "🩲 Ichki kiyimlar":
        await state.set_state(ShoppingState.weight_only)
        await callback.message.edit_text(
            "🩲 **Ichki kiyimlar bo'limi**\n\nIltimos, hozirgi vazningizni kiriting (kg hisobida, masalan: `70`):", 
            parse_mode="Markdown", reply_markup=get_only_back_inline("to_gender")
        )
    else:
        if callback.data == "gender:bola":
            await state.set_state(ShoppingState.child_height)
            await callback.message.edit_text(
                "👶 **Bolalar kiyimi bo'limi**\n\nIltimos, bolaning bo'yini kiriting (sm hisobida, masalan: `95`):", 
                parse_mode="Markdown", reply_markup=get_only_back_inline("to_gender")
            )
        else:
            await state.set_state(ShoppingState.adult_height)
            await callback.message.edit_text(
                f"✨ **{category} ({chosen_gender})**\n\n👇 **Iltimos, bo'yingizni kiriting (sm):**", 
                parse_mode="Markdown", reply_markup=get_only_back_inline("to_gender")
            )

# ↩️ PARAMETRDAN JINS TANLASHGA ORQAGA QAYTISH
@dp.callback_query(F.data == "back:to_gender")
async def back_to_gender_selection(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get('category', "👕 Ustki kiyimlar")
    
    await state.set_state(ShoppingState.gender)
    await callback.message.edit_text(
        text=f"» **Bo'lim:** {category}\n\n**Kim uchun mahsulot qidiryapsiz?** 👇",
        parse_mode="Markdown",
        reply_markup=get_gender_inline()
    )

# 3-BOSQICH: MATNLI JAVOBLARNI TEKSHIRISH VA HISOB-KITOB
@dp.message(ShoppingState.foot_size)
async def calc_foot_size(message: types.Message, state: FSMContext):
    try:
        foot_sm = float(message.text)
        size = "40" if 25.0 <= foot_sm < 26.0 else "41-42" if 26.0 <= foot_sm < 27.0 else "39" if 24.0 <= foot_sm < 25.0 else "43" if 27.0 <= foot_sm < 28.0 else "37" if 23.0 <= foot_sm < 24.0 else "35-36" if foot_sm < 23.0 else "44-45"
        await show_receipt(message, state, f"{size} o'lcham", f"{foot_sm} sm")
    except ValueError:
        await message.answer("⚠️ Iltimos, o'lchamni raqamda kiriting (masalan: 26.5):", reply_markup=get_only_back_inline("to_gender"))

@dp.message(ShoppingState.weight_only)
async def calc_weight_only(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        size = "S" if weight <= 55 else "M" if weight <= 68 else "L" if weight <= 80 else "XL" if weight <= 92 else "XXL"
        await show_receipt(message, state, size, f"{weight} kg")
    except ValueError:
        await message.answer("⚠️ Iltimos, vaznni faqat butun raqamda kiriting:", reply_markup=get_only_back_inline("to_gender"))

@dp.message(ShoppingState.child_height)
async def calc_child_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        size = "56 (0-3 oy)" if height <= 56 else "68 (6-9 oy)" if height <= 68 else "80 (1 yosh)" if height <= 80 else "98 (3 yosh)" if height <= 98 else "116 (5-6 yosh)" if height <= 116 else "128 (7-8 yosh)"
        await show_receipt(message, state, size, f"{height} sm")
    except ValueError:
        await message.answer("⚠️ Iltimos, bo'yni butun raqamda kiriting:", reply_markup=get_only_back_inline("to_gender"))

@dp.message(ShoppingState.adult_height)
async def get_adult_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        await state.update_data(height=height)
        await state.set_state(ShoppingState.adult_weight)
        await message.answer("👇 **Endi esa vazningizni kiriting (kg):**", parse_mode="Markdown", reply_markup=get_only_back_inline("to_gender"))
    except ValueError:
        await message.answer("⚠️ Iltimos, bo'yingizni faqat raqamda kiriting:", reply_markup=get_only_back_inline("to_gender"))

@dp.message(ShoppingState.adult_weight)
async def calc_adult_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        user_data = await state.get_data()
        height = user_data['height']
        gender = user_data['gender']
        category = user_data['category']
        
        size = "S" if weight <= 60 else "M" if 61 <= weight <= 73 else "L" if 74 <= weight <= 85 else "XL" if 86 <= weight <= 95 else "XXL"
        if category == "👖 Shim va shortilar" and gender == "🚹 Erkaklar":
            size = "28-29" if size == "S" else "30-31" if size == "M" else "32-33" if size == "L" else "34-36" if size == "XL" else "38+"

        await show_receipt(message, state, size, f"{height} sm / {weight} kg")
    except ValueError:
        await message.answer("⚠️ Iltimos, vazningizni faqat raqamda kiriting:", reply_markup=get_only_back_inline("to_gender"))

# YAKUNIY RECEPT
async def show_receipt(message: types.Message, state: FSMContext, size, params):
    user_data = await state.get_data()
    category = user_data['category']
    gender = user_data['gender']
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Katalogni ko'rish 🛍", callback_data="view_catalog")
    builder.button(text="Boshqatdan hisoblash 🔄", callback_data="back:to_categories")
    builder.adjust(1, 1)
    
    summary = (
        f"📋 ━━━━ **BUYURTMA CHEKI** ━━━━\n\n"
        f"🗂 **Bo'lim:** {category}\n"
        f"👤 **Kim uchun:** {gender}\n"
        f"📏 **Kiritilgan parametr:** {params}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ **Tavsiya etilgan o'lcham: {size}**\n\n"
        f"Ushbu o'lchamdagi mahsulotlarni ko'rishni istaysizmi?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=builder.as_markup())
    await state.clear()

@dp.callback_query(F.data == "view_catalog")
async def view_catalog_handler(callback: types.CallbackQuery):
    await callback.answer("Katalog tez orada yuklanadi...", show_alert=True)

# STANDART XATOLIKLAR
@dp.message()
async def invalid_message(message: types.Message):
    await message.answer("⚠️ Iltimos, tizim chalkashmasligi uchun xabarlarning ostidagi tugmalardan foydalaning.")

async def main():
    print("Dinamik 'Orqaga' tizimi ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())A"ADMIN_ID", 8727214154))

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

# 👤 JINSNI TANLASH (INLINE)
def get_gender_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚹 Erkaklar uchun", callback_data="gender:erkak")
    builder.button(text="🚺 Ayollar uchun", callback_data="gender:ayol")
    builder.button(text="👶 Bolalar uchun", callback_data="gender:bola")
    builder.button(text="↩️ Orqaga", callback_data="back:to_categories") # Inline orqaga tugmasi
    builder.adjust(2, 1, 1)
    return builder.as_markup()

# ----------------- HANDLERS -----------------

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear() 
    if message.chat.id == ADMIN_ID:
        admin_matn = (
            "👑 **Xush kelibsiz, Hurmatli Direktor!**\n\n"
            "Siz platformaning bosh boshqaruv paneliga kirdingiz.\n"
            "Quyidagi tugmalar orqali savdo markazini nazorat qiling:"
        )
        await message.answer(admin_matn, parse_mode="Markdown", reply_markup=get_admin_keyboard())
    else:
        await show_customer_menu(message, state)

@dp.message(F.text == "🛍 Xaridor rejimiga o'tish")
async def admin_to_customer(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await show_customer_menu(message, state)

async def show_customer_menu(message: types.Message, state: FSMContext):
    is_admin = (message.chat.id == ADMIN_ID)
    premium_matn = (
        "✨ **Salom! Mukammal uslub olamiga xush kelibsiz!**\n\n"
        "Siz kiyim-kechak va oyoq kiyimlarning onlayn platformasiga kirdingiz.\n\n"
        "📐 Tizimimiz sizning parametrlaringiz (bo'y, vazn, oyoq o'lchami) asosida "
        "aynan sizga mos keladigan o'lchamni aniqlab beradi.\n\n"
        "👇 **Xaridni boshlash uchun quyidagi bo'limlardan birini tanlang:**"
    )
    await message.answer(text=premium_matn, parse_mode="Markdown", reply_markup=get_customer_keyboard(is_admin))
    await state.set_state(ShoppingState.category)

@dp.message(F.text == "👑 Direktor paneliga qaytish")
async def back_to_admin_panel(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN_ID:
        await state.clear()
        await message.answer("👑 **Direktor paneliga qaytdingiz!**", parse_mode="Markdown", reply_markup=get_admin_keyboard())

# KATEGORIYA QABUL QILISH
@dp.message(ShoppingState.category, F.text.in_(["👕 Ustki kiyimlar", "👖 Shim va shortilar", "🩲 Ichki kiyimlar", "👟 Oyoq kiyimlar"]))
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(
        f"» {message.text} bo'limi tanlandi.\n\n"
        f"**Kim uchun mahsulot qidiryapsiz?** 👇", 
        parse_mode="Markdown", 
        reply_markup=get_gender_inline()
    )
    await state.set_state(ShoppingState.gender)

# ↩️ JINSNI TANLASH IJRO ETILGANDA ORQAGA QAYTISH
@dp.callback_query(ShoppingState.gender, F.data == "back:to_categories")
async def back_to_categories_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete() # Inline menyuni o'chiramiz
    await show_customer_menu(callback.message, state) # Bosh menyuni qayta ochamiz

# JINSNI INLINE ORQALI QABUL QILISH
@dp.callback_query(ShoppingState.gender, F.data.startswith("gender:"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender_map = {"erkak": "🚹 Erkaklar uchun", "ayol": "🚺 Ayollar uchun", "bola": "👶 Bolalar uchun"}
    gender_text = gender_map[callback.data.split(":")[1]]
    
    await state.update_data(gender=gender_text)
    user_data = await state.get_data()
    category = user_data['category']
    
    await callback.message.delete()
    
    # Parametrlarni kiritishda ham orqaga qaytish tugmasini (Reply) qo'shamiz
    back_kb = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="↩️ Orqaga")]], resize_keyboard=True)
    
    if category == "👟 Oyoq kiyimlar":
        await callback.message.answer("👟 **Oyoq kiyim bo'limi**\n\nIltimos, oyoq kaftingiz uzunligini santimetrda kiriting (masalan: `26.5`):", parse_mode="Markdown", reply_markup=back_kb)
        await state.set_state(ShoppingState.foot_size)
    elif category == "🩲 Ichki kiyimlar":
        await callback.message.answer("🩲 **Ichki kiyimlar bo'limi**\n\nIltimos, hozirgi vazningizni kiriting (kg hisobida, masalan: `70`):", parse_mode="Markdown", reply_markup=back_kb)
        await state.set_state(ShoppingState.weight_only)
    else:
        if callback.data == "gender:bola":
            await callback.message.answer("👶 **Bolalar kiyimi bo'limi**\n\nIltimos, bolaning bo'yini kiriting (sm hisobida, masalan: `95`):", parse_mode="Markdown", reply_markup=back_kb)
            await state.set_state(ShoppingState.child_height)
        else:
            katalog = "ustki kiyimingiz" if category == "👕 Ustki kiyimlar" else "shimingiz"
            await callback.message.answer(f"Tanlagan {katalog} sizga ideal o'tirishi uchun:\n\n👇 **Bo'yingizni kiriting (sm):**", parse_mode="Markdown", reply_markup=back_kb)
            await state.set_state(ShoppingState.adult_height)

# ↩️ PARAMETRLAR BOSQICHIDA ORQAGA BOSILGANDA KATEGORIYA TANLANGAN JAYGA QAYTISH
@dp.message(F.text == "↩️ Orqaga")
async def back_to_gender_selection(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get('category', "👕 Ustki kiyimlar")
    
    await message.answer(
        f"» {category} bo'limiga qaytdingiz.\n\n"
        f"**Kim uchun mahsulot qidiryapsiz?** 👇", 
        parse_mode="Markdown", 
        reply_markup=get_gender_inline()
    )
    await state.set_state(ShoppingState.gender)

# PARAMETRLAR VA HISOB-KITOB
@dp.message(ShoppingState.foot_size)
async def calc_foot_size(message: types.Message, state: FSMContext):
    try:
        foot_sm = float(message.text)
        if foot_sm < 23.0: size = "35-36"
        elif 23.0 <= foot_sm < 24.0: size = "37"
        elif 24.0 <= foot_sm < 25.0: size = "39"
        elif 25.0 <= foot_sm < 26.0: size = "40"
        elif 26.0 <= foot_sm < 27.0: size = "41-42"
        elif 27.0 <= foot_sm < 28.0: size = "43"
        else: size = "44-45"
        await show_receipt(message, state, f"{size} o'lcham", f"{foot_sm} sm")
    except ValueError:
        await message.answer("⚠️ Iltimos, o'lchamni raqamda kiriting (masalan: 26.5):")

@dp.message(ShoppingState.weight_only)
async def calc_weight_only(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        if weight <= 55: size = "S"
        elif weight <= 68: size = "M"
        elif weight <= 80: size = "L"
        elif weight <= 92: size = "XL"
        else: size = "XXL"
        await show_receipt(message, state, size, f"{weight} kg")
    except ValueError:
        await message.answer("⚠️ Iltimos, vaznni faqat butun raqamda kiriting:")

@dp.message(ShoppingState.child_height)
async def calc_child_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        if height <= 56: size = "56 (0-3 oy)"
        elif height <= 68: size = "68 (6-9 oy)"
        elif height <= 80: size = "80 (1 yosh)"
        elif height <= 98: size = "98 (3 yosh)"
        elif height <= 116: size = "116 (5-6 yosh)"
        else: size = "128 (7-8 yosh)"
        await show_receipt(message, state, size, f"{height} sm")
    except ValueError:
        await message.answer("⚠️ Iltimos, bo'yni butun raqamda kiriting:")

@dp.message(ShoppingState.adult_height)
async def get_adult_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        await state.update_data(height=height)
        # Vazn so'rayotganda ham pastda orqaga tugmasi turaveradi
        await message.answer("👇 **Endi esa vazningizni kiriting (kg):**", parse_mode="Markdown")
        await state.set_state(ShoppingState.adult_weight)
    except ValueError:
        await message.answer("⚠️ Iltimos, bo'yingizni faqat raqamda kiriting:")

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
        await message.answer("⚠️ Iltimos, vazningizni faqat raqamda kiriting:")

# YAKUNIY CHEK
async def show_receipt(message: types.Message, state: FSMContext, size, params):
    user_data = await state.get_data()
    category = user_data['category']
    gender = user_data['gender']
    is_admin = (message.chat.id == ADMIN_ID)
    
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Katalogni ko'rish 🛍"), types.KeyboardButton(text="Boshqatdan hisoblash 🔄")]],
        resize_keyboard=True
    )
    
    summary = (
        f"📋 ━━━━ **BUYURTMA CHEKI** ━━━━\n\n"
        f"🗂 **Bo'lim:** {category}\n"
        f"👤 **Kim uchun:** {gender}\n"
        f"📏 **Kiritilgan parametr:** {params}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ **Tavsiya etilgan o'lcham: {size}**\n\n"
        f"Ushbu o'lchamdagi mahsulotlarni ko'rishni istaysizmi?"
    )
    await message.answer(summary, parse_mode="Markdown", reply_markup=markup)
    await state.clear()

@dp.message(F.text == "Boshqatdan hisoblash 🔄")
async def restart_calculation(message: types.Message, state: FSMContext):
    await show_customer_menu(message, state)

# STANDART XATOLIKLAR
@dp.message()
async def invalid_message(message: types.Message):
    await message.answer("⚠️ Iltimos, tizim tushunishi uchun menyudagi tugmalardan foydalaning.")

async def main():
    print("Orqaga tugmasi sozlangan professional bot Railway'da...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
