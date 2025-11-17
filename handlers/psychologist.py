from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import PsychologistStates
from keyboards import (
    psychologist_main_menu,
    create_messages_inline_keyboard,
    create_reply_keyboard,
    create_appointments_inline_keyboard,
    create_appointment_actions_keyboard
)
import database as db
from config import PSYCHOLOGIST_ID

router = Router()


def is_psychologist(user_id: int) -> bool:
    """Check if user is the psychologist"""
    return user_id == PSYCHOLOGIST_ID


@router.message(Command("start"))
async def psychologist_start(message: Message, state: FSMContext):
    """Handle /start command for psychologist"""
    if not is_psychologist(message.from_user.id):
        return

    await state.clear()
    welcome_text = (
        "👨‍⚕️ <b>Psychologist Dashboard</b>\n\n"
        "Welcome! Here you can:\n\n"
        "📬 View and reply to student messages\n"
        "📅 Manage appointment requests\n"
        "📊 View statistics\n\n"
        "Use the menu below to navigate."
    )

    await message.answer(
        welcome_text,
        reply_markup=psychologist_main_menu(),
        parse_mode="HTML"
    )


# MESSAGES MANAGEMENT
@router.message(F.text == "📬 View Messages")
async def view_messages(message: Message, state: FSMContext):
    """View unreplied messages"""
    if not is_psychologist(message.from_user.id):
        return

    messages = await db.get_unreplied_messages()

    if not messages:
        await message.answer(
            "📭 No unreplied messages at the moment.",
            reply_markup=psychologist_main_menu()
        )
        return

    await message.answer(
        f"📬 <b>Unreplied Messages ({len(messages)})</b>\n\n"
        "Select a message to view and reply:",
        reply_markup=create_messages_inline_keyboard(messages),
        parse_mode="HTML"
    )
    await state.set_state(PsychologistStates.viewing_messages)


@router.callback_query(F.data.startswith("msg_"))
async def show_message_detail(callback: CallbackQuery, state: FSMContext):
    """Show message details"""
    if not is_psychologist(callback.from_user.id):
        return

    message_id = int(callback.data.split("_")[1])
    msg = await db.get_message_by_id(message_id)

    if not msg:
        await callback.answer("Message not found")
        return

    user = await db.get_user_by_id(msg['user_id'])

    if msg['is_anonymous']:
        detail_text = (
            f"📬 <b>Message Details</b>\n\n"
            f"ID: {msg['id']}\n"
            f"From: Anonymous\n"
            f"Date: {msg['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
            f"<b>Message:</b>\n{msg['message_text']}"
        )
    else:
        detail_text = (
            f"📬 <b>Message Details</b>\n\n"
            f"ID: {msg['id']}\n"
            f"From: {user['full_name'] if user else 'N/A'}\n"
            f"Student ID: {user['student_id'] if user else 'N/A'}\n"
            f"Username: @{user['username'] if user and user['username'] else 'N/A'}\n"
            f"Date: {msg['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
            f"<b>Message:</b>\n{msg['message_text']}"
        )

    await callback.message.edit_text(
        detail_text,
        reply_markup=create_reply_keyboard(msg['id']),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reply_"))
async def start_reply(callback: CallbackQuery, state: FSMContext):
    """Start replying to a message"""
    if not is_psychologist(callback.from_user.id):
        return

    message_id = int(callback.data.split("_")[1])
    await state.update_data(reply_to_message_id=message_id)

    await callback.message.answer(
        "✍️ <b>Reply to Message</b>\n\n"
        "Type your reply below. It will be sent to the student.",
        parse_mode="HTML"
    )
    await state.set_state(PsychologistStates.replying_to_message)
    await callback.answer()


@router.message(StateFilter(PsychologistStates.replying_to_message))
async def process_reply(message: Message, state: FSMContext):
    """Process and send reply to student"""
    if not is_psychologist(message.from_user.id):
        return

    data = await state.get_data()
    message_id = data.get('reply_to_message_id')

    # Save reply
    replied_msg = await db.reply_to_message(message_id, message.text)

    if not replied_msg:
        await message.answer("Error: Message not found")
        return

    # Get user to send reply
    user = await db.get_user_by_id(replied_msg['user_id'])

    if user:
        try:
            notification = (
                f"💬 <b>Reply from Psychologist</b>\n\n"
                f"<i>{message.text}</i>\n\n"
                f"If you need further assistance, feel free to send another message."
            )
            await message.bot.send_message(user['telegram_id'], notification, parse_mode="HTML")
            await message.answer(
                "✅ Reply sent successfully!",
                reply_markup=psychologist_main_menu()
            )
        except Exception as e:
            await message.answer(
                f"❌ Error sending reply: {e}\n"
                "However, the reply has been saved.",
                reply_markup=psychologist_main_menu()
            )
    else:
        await message.answer(
            "❌ User not found. Reply saved but not delivered.",
            reply_markup=psychologist_main_menu()
        )

    await state.clear()


@router.callback_query(F.data == "back_to_messages")
async def back_to_messages(callback: CallbackQuery, state: FSMContext):
    """Go back to messages list"""
    if not is_psychologist(callback.from_user.id):
        return

    messages = await db.get_unreplied_messages()

    if not messages:
        await callback.message.edit_text("📭 No unreplied messages at the moment.")
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📬 <b>Unreplied Messages ({len(messages)})</b>\n\n"
        "Select a message to view and reply:",
        reply_markup=create_messages_inline_keyboard(messages),
        parse_mode="HTML"
    )
    await callback.answer()


# APPOINTMENTS MANAGEMENT
@router.message(F.text == "📅 Manage Appointments")
async def manage_appointments(message: Message, state: FSMContext):
    """View and manage appointments"""
    if not is_psychologist(message.from_user.id):
        return

    appointments = await db.get_all_appointments()

    if not appointments:
        await message.answer(
            "📭 No appointments at the moment.",
            reply_markup=psychologist_main_menu()
        )
        return

    await message.answer(
        f"📅 <b>All Appointments ({len(appointments)})</b>\n\n"
        "Select an appointment to manage:",
        reply_markup=create_appointments_inline_keyboard(appointments),
        parse_mode="HTML"
    )
    await state.set_state(PsychologistStates.managing_appointments)


@router.callback_query(F.data.startswith("apt_"))
async def show_appointment_detail(callback: CallbackQuery, state: FSMContext):
    """Show appointment details"""
    if not is_psychologist(callback.from_user.id):
        return

    appointment_id = int(callback.data.split("_")[1])
    appointment = await db.get_appointment_by_id(appointment_id)

    if not appointment:
        await callback.answer("Appointment not found")
        return

    status_emoji = {
        'pending': '🕐 Pending',
        'confirmed': '✅ Confirmed',
        'cancelled': '❌ Cancelled',
        'completed': '✔️ Completed'
    }.get(appointment['status'], '❓ Unknown')

    detail_text = (
        f"📅 <b>Appointment Details</b>\n\n"
        f"ID: {appointment['id']}\n"
        f"Status: {status_emoji}\n\n"
        f"👤 Name: {appointment['full_name']}\n"
        f"🆔 Student ID: {appointment['student_id']}\n"
        f"📆 Preferred Date: {appointment['preferred_date']}\n"
        f"🕐 Preferred Time: {appointment['preferred_time']}\n"
        f"📝 Reason: {appointment['reason']}\n"
        f"📅 Created: {appointment['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
    )

    if appointment['notes']:
        detail_text += f"\n📌 Notes: {appointment['notes']}"

    await callback.message.edit_text(
        detail_text,
        reply_markup=create_appointment_actions_keyboard(appointment['id']),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_appointment(callback: CallbackQuery, state: FSMContext):
    """Confirm an appointment"""
    if not is_psychologist(callback.from_user.id):
        return

    appointment_id = int(callback.data.split("_")[1])
    apt = await db.update_appointment_status(appointment_id, "confirmed")

    if apt:
        user = await db.get_user_by_id(apt['user_id'])
        if user:
            try:
                notification = (
                    f"✅ <b>Appointment Confirmed!</b>\n\n"
                    f"Your appointment has been confirmed:\n"
                    f"📆 Date: {apt['preferred_date']}\n"
                    f"🕐 Time: {apt['preferred_time']}\n\n"
                    f"Please arrive on time. Looking forward to seeing you!"
                )
                await callback.bot.send_message(user['telegram_id'], notification, parse_mode="HTML")
            except Exception as e:
                print(f"Error notifying user: {e}")

        await callback.answer("✅ Appointment confirmed!")
        await back_to_appointments(callback, state)
    else:
        await callback.answer("❌ Error confirming appointment")


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_appointment(callback: CallbackQuery, state: FSMContext):
    """Cancel an appointment"""
    if not is_psychologist(callback.from_user.id):
        return

    appointment_id = int(callback.data.split("_")[1])
    apt = await db.update_appointment_status(appointment_id, "cancelled")

    if apt:
        user = await db.get_user_by_id(apt['user_id'])
        if user:
            try:
                notification = (
                    f"❌ <b>Appointment Cancelled</b>\n\n"
                    f"Unfortunately, your appointment for {apt['preferred_date']} "
                    f"at {apt['preferred_time']} has been cancelled.\n\n"
                    f"Please feel free to book another appointment or send a message "
                    f"if you need assistance."
                )
                await callback.bot.send_message(user['telegram_id'], notification, parse_mode="HTML")
            except Exception as e:
                print(f"Error notifying user: {e}")

        await callback.answer("❌ Appointment cancelled")
        await back_to_appointments(callback, state)
    else:
        await callback.answer("❌ Error cancelling appointment")


@router.callback_query(F.data.startswith("complete_"))
async def complete_appointment(callback: CallbackQuery, state: FSMContext):
    """Mark appointment as completed"""
    if not is_psychologist(callback.from_user.id):
        return

    appointment_id = int(callback.data.split("_")[1])
    apt = await db.update_appointment_status(appointment_id, "completed")

    if apt:
        await callback.answer("✔️ Appointment marked as completed")
        await back_to_appointments(callback, state)
    else:
        await callback.answer("❌ Error updating appointment")


@router.callback_query(F.data == "back_to_appointments")
async def back_to_appointments(callback: CallbackQuery, state: FSMContext):
    """Go back to appointments list"""
    if not is_psychologist(callback.from_user.id):
        return

    appointments = await db.get_all_appointments()

    if not appointments:
        await callback.message.edit_text("📭 No appointments at the moment.")
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📅 <b>All Appointments ({len(appointments)})</b>\n\n"
        "Select an appointment to manage:",
        reply_markup=create_appointments_inline_keyboard(appointments),
        parse_mode="HTML"
    )
    await callback.answer()


# STATISTICS
@router.message(F.text == "📊 Statistics")
async def show_statistics(message: Message):
    """Show statistics"""
    if not is_psychologist(message.from_user.id):
        return

    messages = await db.get_unreplied_messages()
    all_appointments = await db.get_all_appointments()
    pending_appointments = await db.get_pending_appointments()

    confirmed = len([a for a in all_appointments if a.status == 'confirmed'])
    completed = len([a for a in all_appointments if a.status == 'completed'])
    cancelled = len([a for a in all_appointments if a.status == 'cancelled'])

    stats_text = (
        f"📊 <b>Statistics</b>\n\n"
        f"📬 <b>Messages:</b>\n"
        f"• Unreplied: {len(messages)}\n\n"
        f"📅 <b>Appointments:</b>\n"
        f"• Total: {len(all_appointments)}\n"
        f"• Pending: {len(pending_appointments)}\n"
        f"• Confirmed: {confirmed}\n"
        f"• Completed: {completed}\n"
        f"• Cancelled: {cancelled}"
    )

    await message.answer(stats_text, parse_mode="HTML")


# QUICK REPLY COMMAND
@router.message(Command("reply"))
async def quick_reply_command(message: Message, state: FSMContext):
    """Quick reply using command /reply <message_id>"""
    if not is_psychologist(message.from_user.id):
        return

    try:
        message_id = int(message.text.split()[1])
        msg = await db.get_message_by_id(message_id)

        if not msg:
            await message.answer("❌ Message not found")
            return

        if msg.replied:
            await message.answer("⚠️ This message has already been replied to")
            return

        await state.update_data(reply_to_message_id=message_id)
        await message.answer(
            f"✍️ Replying to message ID: {message_id}\n\n"
            "Type your reply below:",
            parse_mode="HTML"
        )
        await state.set_state(PsychologistStates.replying_to_message)

    except (IndexError, ValueError):
        await message.answer(
            "❌ Invalid format. Use: /reply <message_id>\n"
            "Example: /reply 123"
        )


# APPOINTMENTS COMMAND
@router.message(Command("appointments"))
async def appointments_command(message: Message, state: FSMContext):
    """Quick access to appointments"""
    if not is_psychologist(message.from_user.id):
        return

    await manage_appointments(message, state)
