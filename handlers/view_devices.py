from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import func, select

from database import async_session_maker, Phone, Computer, SimCard
from keyboards.main_kb import (
    device_type_kb,
    pagination_kb,
    main_menu_kb,
    confirm_delete_kb,
)

router = Router()

PAGE_SIZE = 10

MODEL_MAP = {
    "phones": (Phone, "📱 Telefonlar", "phone"),
    "computers": (Computer, "💻 Kompyuterlar", "computer"),
    "sims": (SimCard, "📶 SIM kartalar", "sim"),
}

PREFIX_MODEL = {
    "phone": Phone,
    "computer": Computer,
    "sim": SimCard,
}

MODEL_PREFIX_LABEL = {
    "phone": "📱 Telefon",
    "computer": "💻 Kompyuter",
    "sim": "📶 SIM karta",
}

class EditDeviceFSM(StatesGroup):
    waiting_owner = State()
    waiting_device_name = State()
    waiting_note = State()


@router.callback_query(F.data == "view_devices")
async def view_devices_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 Qaysi bo'limni ko'rmoqchisiz?",
        reply_markup=device_type_kb("view"),
    )
    await callback.answer()


@router.callback_query(F.data == "edit_devices")
async def edit_devices_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "✏️ O'zgartirish uchun qurilma turini tanlang:",
        reply_markup=device_type_kb("edit"),
    )
    await callback.answer()


async def render_page(callback: CallbackQuery, model_key: str, page: int):
    model, title, prefix = MODEL_MAP[model_key]

    async with async_session_maker() as session:
        total_result = await session.execute(select(func.count()).select_from(model))
        total = total_result.scalar() or 0

        if total == 0:
            await callback.message.edit_text(
                f"{title} bo'limi bo'sh.",
                reply_markup=pagination_kb(0, 1, prefix),
            )
            await callback.answer()
            return

        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        page = max(0, min(page, total_pages - 1))

        result = await session.execute(select(model).order_by(model.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE))
        items = result.scalars().all()

    lines = [f"<b>{title}</b> (jami: {total} ta)\n"]
    for i, item in enumerate(items, start=page * PAGE_SIZE + 1):
        note = f"\n   Izoh: {item.note}" if item.note else ""
        lines.append(f"{i}. <b>{item.device_name}</b> — {item.owner_name}{note}")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=pagination_kb(page, total_pages, prefix),
    )
    await callback.answer()


@router.callback_query(F.data == "view_phones")
async def view_phones(callback: CallbackQuery):
    await render_page(callback, "phones", 0)


@router.callback_query(F.data == "view_computers")
async def view_computers(callback: CallbackQuery):
    await render_page(callback, "computers", 0)


@router.callback_query(F.data == "view_sims")
async def view_sims(callback: CallbackQuery):
    await render_page(callback, "sims", 0)


@router.callback_query(F.data.startswith("phone_page_"))
async def phone_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await render_page(callback, "phones", page)


@router.callback_query(F.data.startswith("computer_page_"))
async def computer_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await render_page(callback, "computers", page)


@router.callback_query(F.data.startswith("sim_page_"))
async def sim_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await render_page(callback, "sims", page)


@router.callback_query(F.data == "edit_phones")
async def edit_phones(callback: CallbackQuery):
    await render_edit_page(callback, "phones", 0)


@router.callback_query(F.data == "edit_computers")
async def edit_computers(callback: CallbackQuery):
    await render_edit_page(callback, "computers", 0)


@router.callback_query(F.data == "edit_sims")
async def edit_sims(callback: CallbackQuery):
    await render_edit_page(callback, "sims", 0)


@router.callback_query(F.data.startswith("edit_phone_page_"))
async def edit_phone_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await render_edit_page(callback, "phones", page)


@router.callback_query(F.data.startswith("edit_computer_page_"))
async def edit_computer_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await render_edit_page(callback, "computers", page)


@router.callback_query(F.data.startswith("edit_sim_page_"))
async def edit_sim_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await render_edit_page(callback, "sims", page)


async def render_edit_page(callback: CallbackQuery, model_key: str, page: int):
    model, title, prefix = MODEL_MAP[model_key]

    async with async_session_maker() as session:
        total_result = await session.execute(select(func.count()).select_from(model))
        total = total_result.scalar() or 0

        if total == 0:
            await callback.message.edit_text(
                f"{title} bo'limi bo'sh.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Orqaga", callback_data="edit_devices")]]),
            )
            await callback.answer()
            return

        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        page = max(0, min(page, total_pages - 1))

        result = await session.execute(select(model).order_by(model.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE))
        items = result.scalars().all()

    lines = [f"<b>{title}</b> (jami: {total} ta)\n"]
    start_index = page * PAGE_SIZE + 1
    for i, item in enumerate(items, start=start_index):
        note = f"\n   Izoh: {item.note}" if item.note else ""
        lines.append(f"{i}. <b>{item.device_name}</b> — {item.owner_name}{note}")

    keyboard_rows = []
    for i, item in enumerate(items, start=start_index):
        keyboard_rows.append([
            InlineKeyboardButton(text=f"{i} - {item.device_name[:12]}", callback_data=f"edit_item_{prefix}_{item.id}"),
        ])

    page_row = []
    if page > 0:
        page_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"edit_{model_key[:-1]}_page_{page - 1}"))
    page_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        page_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"edit_{model_key[:-1]}_page_{page + 1}"))
    if page_row:
        keyboard_rows.append(page_row)

    keyboard_rows.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="edit_devices")])

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_item_"))
async def do_edit_item(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 3)
    if len(parts) != 4 or parts[0] != "edit" or parts[1] != "item":
        await callback.answer("Noto'g'ri buyruq")
        return

    prefix = parts[2]
    item_id = int(parts[3])

    if prefix not in PREFIX_MODEL:
        await callback.answer("Noto'g'ri qurilma turi")
        return

    await state.update_data(model_prefix=prefix, item_id=item_id)
    await state.set_state(EditDeviceFSM.waiting_owner)
    await callback.message.edit_text("✏️ Yangi egani (F.I.SH.) kiriting:")
    await callback.answer()


@router.message(EditDeviceFSM.waiting_owner)
async def edit_owner(message: Message, state: FSMContext):
    await state.update_data(owner_name=message.text.strip())
    await state.set_state(EditDeviceFSM.waiting_device_name)
    await message.answer("✏️ Yangi qurilma nomini kiriting:")


@router.message(EditDeviceFSM.waiting_device_name)
async def edit_device_name(message: Message, state: FSMContext):
    await state.update_data(device_name=message.text.strip())
    await state.set_state(EditDeviceFSM.waiting_note)
    await message.answer("📝 Yangi izohni kiriting (bo'sh qoldirish mumkin):")


@router.message(EditDeviceFSM.waiting_note)
async def edit_note(message: Message, state: FSMContext):
    data = await state.get_data()
    prefix = data.get("model_prefix")
    item_id = data.get("item_id")
    model = PREFIX_MODEL[prefix]
    owner_name = data.get("owner_name")
    device_name = data.get("device_name")
    note = message.text.strip() if message.text else None

    async with async_session_maker() as session:
        obj = await session.get(model, item_id)
        if obj:
            obj.owner_name = owner_name
            obj.device_name = device_name
            obj.note = note
            await session.commit()

    await state.clear()
    await message.answer(
        "✅ Qurilma ma'lumotlari yangilandi!\n"
        f"Turi: {MODEL_PREFIX_LABEL[prefix]}\n"
        f"Egasi: {owner_name}\n"
        f"Qurilma: {device_name}\n"
        f"Izoh: {note or '—'}",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data.startswith("remove_"))
async def request_remove(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    if len(parts) != 3 or parts[0] != "remove":
        await callback.answer("Noto'g'ri buyruq")
        return

    prefix = parts[1]
    item_id = int(parts[2])
    if prefix not in PREFIX_MODEL:
        await callback.answer("Noto'g'ri tur")
        return

    await callback.message.edit_text(
        "🗑️ Rostdan o'chirishni xohlaysizmi?",
        reply_markup=confirm_delete_kb(prefix, item_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    parts = callback.data.split("_", 3)
    if len(parts) != 4 or parts[0] != "confirm" or parts[1] != "delete":
        await callback.answer("Noto'g'ri buyruq")
        return

    prefix = parts[2]
    item_id = int(parts[3])
    if prefix not in PREFIX_MODEL:
        await callback.answer("Noto'g'ri tur")
        return

    model = PREFIX_MODEL[prefix]
    async with async_session_maker() as session:
        obj = await session.get(model, item_id)
        if obj:
            await session.delete(obj)
            await session.commit()

    await callback.message.edit_text("✅ Qurilma o'chirildi.", reply_markup=device_type_kb("view"))
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_delete_"))
async def cancel_delete(callback: CallbackQuery):
    await callback.message.edit_text("❌ O'chirish bekor qilindi.", reply_markup=device_type_kb("view"))
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()