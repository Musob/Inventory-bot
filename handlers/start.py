from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards.main_kb import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Salom, {message.from_user.full_name}!\n\n"
        "📋 Inventarizatsiya botiga xush kelibsiz.\n"
        "Quyidagi menyudan kerakli amalni tanlang:",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Asosiy menyu:",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()