from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi qurilma qo'shish", callback_data="add_device")],
        [InlineKeyboardButton(text="📦 Qurilmalar", callback_data="view_devices")],
        [InlineKeyboardButton(text="✏️ O'zgartirish", callback_data="edit_devices")],
    ])


def device_type_kb(action: str) -> InlineKeyboardMarkup:
    """action: 'add', 'view' yoki 'edit'"""
    if action == "add":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Telefon", callback_data="add_phone")],
            [InlineKeyboardButton(text="💻 Kompyuter", callback_data="add_computer")],
            [InlineKeyboardButton(text="📶 SIM karta", callback_data="add_sim")],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")],
        ])
    elif action == "edit":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Telefonlar", callback_data="edit_phones")],
            [InlineKeyboardButton(text="💻 Kompyuterlar", callback_data="edit_computers")],
            [InlineKeyboardButton(text="📶 SIM kartalar", callback_data="edit_sims")],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")],
        ])
    else:  # view
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Telefonlar", callback_data="view_phones")],
            [InlineKeyboardButton(text="💻 Kompyuterlar", callback_data="view_computers")],
            [InlineKeyboardButton(text="📶 SIM kartalar", callback_data="view_sims")],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")],
        ])


def pagination_kb(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    buttons = []
    nav_row = []

    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"{prefix}_page_{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"{prefix}_page_{page + 1}"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="view_devices")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_delete_kb(prefix: str, item_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_{prefix}_{item_id}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_delete_{prefix}_{item_id}")],
    ])