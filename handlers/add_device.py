from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import async_session_maker, Phone, Computer, SimCard
from keyboards.main_kb import device_type_kb, main_menu_kb

router = Router()


class AddDeviceFSM(StatesGroup):
    choose_type = State()
    waiting_owner = State()
    waiting_device_name = State()


DEVICE_LABELS = {
    "phone": "📱 Telefon",
    "computer": "💻 Kompyuter",
    "sim": "📶 SIM karta",
}

DEVICE_PROMPTS = {
    "phone": "📱 Telefon nomini kiriting (masalan: Samsung Galaxy A54):",
    "computer": "💻 Kompyuter nomini kiriting (masalan: HP ProBook 450):",
    "sim": "📶 SIM karta raqamini kiriting (masalan: +998901234567):",
}


@router.callback_query(F.data == "add_device")
async def add_device_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "➕ Qanday turdagi qurilma qo'shmoqchisiz?",
        reply_markup=device_type_kb("add"),
    )
    await callback.answer()


@router.callback_query(F.data.in_({"add_phone", "add_computer", "add_sim"}))
async def add_device_type(callback: CallbackQuery, state: FSMContext):
    device_type = callback.data.replace("add_", "")
    await state.update_data(device_type=device_type)
    await state.set_state(AddDeviceFSM.waiting_owner)
    await callback.message.edit_text(
        f"{DEVICE_LABELS[device_type]} tanlandi.\n\n"
        "✍️ Kim nomiga yozamiz? (F.I.SH. kiriting):"
    )
    await callback.answer()


@router.message(AddDeviceFSM.waiting_owner)
async def add_device_owner(message: Message, state: FSMContext):
    await state.update_data(owner_name=message.text.strip())
    data = await state.get_data()
    device_type = data["device_type"]
    await state.set_state(AddDeviceFSM.waiting_device_name)
    await message.answer(DEVICE_PROMPTS[device_type])


@router.message(AddDeviceFSM.waiting_device_name)
async def add_device_name(message: Message, state: FSMContext):
    data = await state.get_data()
    device_type = data["device_type"]
    owner_name = data["owner_name"]
    device_name = message.text.strip()

    model_map = {
        "phone": Phone,
        "computer": Computer,
        "sim": SimCard,
    }

    async with async_session_maker() as session:
        obj = model_map[device_type](owner_name=owner_name, device_name=device_name)
        session.add(obj)
        await session.commit()

    await state.clear()
    await message.answer(
        f"✅ Muvaffaqiyatli qo'shildi!\n\n"
        f"Turi: {DEVICE_LABELS[device_type]}\n"
        f"Egasi: {owner_name}\n"
        f"Qurilma: {device_name}",
        reply_markup=main_menu_kb(),
    )