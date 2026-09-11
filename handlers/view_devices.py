from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import func, select

from database import async_session_maker, Phone, Computer, SimCard
from keyboards.main_kb import device_type_kb, pagination_kb

router = Router()

PAGE_SIZE = 10  # Har bir sahifada 10 ta yozuv

MODEL_MAP = {
    "phones": (Phone, "📱 Telefonlar", "phone"),
    "computers": (Computer, "💻 Kompyuterlar", "computer"),
    "sims": (SimCard, "📶 SIM kartalar", "sim"),
}


@router.callback_query(F.data == "view_devices")
async def view_devices_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 Qaysi bo'limni ko'rmoqchisiz?",
        reply_markup=device_type_kb("view"),
    )
    await callback.answer()


async def render_page(callback: CallbackQuery, model_key: str, page: int):
    model, title, prefix = MODEL_MAP[model_key]

    async with async_session_maker() as session:
        # Umumiy soni
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

        # Sahifadagi yozuvlar
        result = await session.execute(
            select(model).order_by(model.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE)
        )
        items = result.scalars().all()

    lines = [f"<b>{title}</b> (jami: {total} ta)\n"]
    for i, item in enumerate(items, start=page * PAGE_SIZE + 1):
        lines.append(f"{i}. <b>{item.device_name}</b> — {item.owner_name}")

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


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()