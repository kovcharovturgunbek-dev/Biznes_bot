from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Mahsulotlar")],
            [KeyboardButton(text="🔎 Qidirish")],
            [KeyboardButton(text="🛒 Savatim"),
             KeyboardButton(text="📦 Buyurtmalarim")],
            [KeyboardButton(text="❤️ Sevimlilar"),
             KeyboardButton(text="👤 Profilim")],
            [KeyboardButton(text="🎁 Aksiyalar")],
            [KeyboardButton(text="🏪 Sotuvchi bo‘lish")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo‘limni tanlang..."
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Assalomu alaykum! Bozorchi marketplace'iga xush kelibsiz! 🛍\n\n"
        "Xarid qilish yoki sotuvchi bo‘lish uchun quyidagi menyudan foydalaning.",
        reply_markup=main_menu()
    )
