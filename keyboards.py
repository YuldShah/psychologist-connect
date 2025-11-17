from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard():
    """Main menu for students"""
    keyboard = [
        [KeyboardButton(text="📅 Book Appointment")],
        [KeyboardButton(text="💬 Online Chat")],
        [KeyboardButton(text="ℹ️ About")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def chat_type_keyboard():
    """Choose between anonymous or identified chat"""
    keyboard = [
        [KeyboardButton(text="🎭 Anonymous Chat")],
        [KeyboardButton(text="👤 Share My Information")],
        [KeyboardButton(text="🔙 Back to Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def cancel_keyboard():
    """Cancel button"""
    keyboard = [
        [KeyboardButton(text="❌ Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def psychologist_main_menu():
    """Main menu for psychologist"""
    keyboard = [
        [KeyboardButton(text="📬 View Messages")],
        [KeyboardButton(text="📅 Manage Appointments")],
        [KeyboardButton(text="📊 Statistics")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def create_messages_inline_keyboard(messages, page=1, per_page=5):
    """Create inline keyboard for messages with pagination"""
    keyboard = []

    # Calculate pagination
    total_messages = len(messages)
    total_pages = (total_messages + per_page - 1) // per_page  # Ceiling division
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_messages)

    # Add message buttons for current page
    for msg in messages[start_idx:end_idx]:
        user_info = "👤 Anon" if msg['is_anonymous'] else f"📝 #{msg['id']}"
        # Shorten to 15 characters
        preview = msg['message_text'][:15] + "..." if len(msg['message_text']) > 15 else msg['message_text']
        keyboard.append([
            InlineKeyboardButton(
                text=f"{user_info} - {preview}",
                callback_data=f"msg_{msg['id']}"
            )
        ])

    # Add pagination buttons if needed
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text="◀️ Previous", callback_data=f"msg_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="msg_page_info"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"msg_page_{page+1}"))
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_reply_keyboard(message_id):
    """Create keyboard for replying to a message"""
    keyboard = [
        [InlineKeyboardButton(text="✍️ Reply", callback_data=f"reply_{message_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_messages")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_appointments_inline_keyboard(appointments, page=1, per_page=5):
    """Create inline keyboard for appointments with pagination"""
    keyboard = []

    # Calculate pagination
    total_appointments = len(appointments)
    total_pages = (total_appointments + per_page - 1) // per_page  # Ceiling division
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_appointments)

    # Add appointment buttons for current page
    for apt in appointments[start_idx:end_idx]:
        status_emoji = {
            'pending': '🕐',
            'confirmed': '✅',
            'cancelled': '❌',
            'completed': '✔️'
        }.get(apt['status'], '❓')

        # Shorten name if needed
        name = apt['full_name'][:20] + "..." if len(apt['full_name']) > 20 else apt['full_name']

        keyboard.append([
            InlineKeyboardButton(
                text=f"{status_emoji} {name} - {apt['preferred_date']}",
                callback_data=f"apt_{apt['id']}"
            )
        ])

    # Add pagination buttons if needed
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text="◀️ Previous", callback_data=f"apt_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="apt_page_info"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"apt_page_{page+1}"))
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_appointment_actions_keyboard(appointment_id):
    """Create keyboard for appointment actions"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{appointment_id}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_{appointment_id}")],
        [InlineKeyboardButton(text="✔️ Complete", callback_data=f"complete_{appointment_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_appointments")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
