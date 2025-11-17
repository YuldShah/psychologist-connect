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


def create_messages_inline_keyboard(messages):
    """Create inline keyboard for messages"""
    keyboard = []
    for msg in messages:
        user_info = "Anonymous" if msg['is_anonymous'] else f"ID: {msg['id']}"
        preview = msg['message_text'][:30] + "..." if len(msg['message_text']) > 30 else msg['message_text']
        keyboard.append([
            InlineKeyboardButton(
                text=f"{user_info} - {preview}",
                callback_data=f"msg_{msg['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_reply_keyboard(message_id):
    """Create keyboard for replying to a message"""
    keyboard = [
        [InlineKeyboardButton(text="✍️ Reply", callback_data=f"reply_{message_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_messages")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_appointments_inline_keyboard(appointments):
    """Create inline keyboard for appointments"""
    keyboard = []
    for apt in appointments:
        status_emoji = {
            'pending': '🕐',
            'confirmed': '✅',
            'cancelled': '❌',
            'completed': '✔️'
        }.get(apt['status'], '❓')

        keyboard.append([
            InlineKeyboardButton(
                text=f"{status_emoji} {apt['full_name']} - {apt['preferred_date']}",
                callback_data=f"apt_{apt['id']}"
            )
        ])
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
