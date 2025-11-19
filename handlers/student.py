from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import StudentStates
from keyboards import (
    main_menu_keyboard, chat_type_keyboard, cancel_keyboard,
    skip_keyboard, chat_session_keyboard, create_credentials_keyboard
)
import database as db
from config import PSYCHOLOGIST_ID
import validators

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    await db.get_or_create_user(message.from_user.id, message.from_user.username)

    welcome_text = (
        "🎓 <b>Welcome to New Uzbekistan University Psychology Support</b>\n\n"
        "I'm here to help you connect with our university psychologist.\n\n"
        "You can:\n"
        "📅 <b>Book an Appointment</b> - Schedule a face-to-face session\n"
        "💬 <b>Online Chat</b> - Send a message to the psychologist\n\n"
        "All conversations are confidential and professional.\n\n"
        "How would you like to proceed?"
    )

    await message.answer(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="HTML")
    await state.set_state(StudentStates.choosing_service)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """Handle /menu command"""
    await state.clear()
    await message.answer(
        "Main Menu - Choose an option:",
        reply_markup=main_menu_keyboard()
    )
    await state.set_state(StudentStates.choosing_service)


# ONLINE CHAT FLOW
@router.message(F.text == "💬 Online Chat", StateFilter(StudentStates.choosing_service))
async def choose_online_chat(message: Message, state: FSMContext):
    """Handle online chat selection"""
    await message.answer(
        "💬 <b>Online Chat</b>\n\n"
        "You can choose to send your message:\n\n"
        "🎭 <b>Anonymous Chat</b> - Your identity remains private\n"
        "👤 <b>Share My Information</b> - Include your name and student ID\n\n"
        "How would you like to proceed?",
        reply_markup=chat_type_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentStates.choosing_chat_type)


@router.message(F.text == "🎭 Anonymous Chat", StateFilter(StudentStates.choosing_chat_type))
async def anonymous_chat(message: Message, state: FSMContext):
    """Handle anonymous chat selection"""
    await state.update_data(is_anonymous=True)
    await message.answer(
        "🎭 <b>Anonymous Chat</b>\n\n"
        "Your messages will be sent anonymously to the psychologist.\n\n"
        "Type your messages below.\n"
        "When done, click '✅ Done Chatting'",
        reply_markup=chat_session_keyboard()
    )
    await state.set_state(StudentStates.in_chat_session)


@router.message(F.text == "👤 Share My Information", StateFilter(StudentStates.choosing_chat_type))
async def identified_chat(message: Message, state: FSMContext):
    """Handle identified chat selection - check for saved credentials"""
    await state.update_data(is_anonymous=False)

    # Check if user has saved credentials
    user = await db.get_or_create_user(message.from_user.id, message.from_user.username)

    if user.get('full_name'):
        # User has saved credentials - show options
        await message.answer(
            "👤 <b>Share Information</b>\n\n"
            "Would you like to use your previous information or enter new details?",
            reply_markup=create_credentials_keyboard(user['full_name'], user.get('student_id'))
        )
        await state.set_state(StudentStates.choosing_credentials)
    else:
        # No saved credentials - ask for new info
        await message.answer(
            "👤 <b>Share Information</b>\n\n"
            "Please enter your <b>full name</b>:",
            reply_markup=cancel_keyboard()
        )
        await state.set_state(StudentStates.entering_full_name)


# Callback handlers for credential selection
@router.callback_query(F.data == "use_last_credentials", StateFilter(StudentStates.choosing_credentials))
async def use_last_credentials(callback: CallbackQuery, state: FSMContext):
    """Use previously saved credentials"""
    user = await db.get_or_create_user(callback.from_user.id, callback.from_user.username)

    await state.update_data(
        full_name=user['full_name'],
        student_id=user.get('student_id')
    )

    await callback.message.edit_text(
        f"✅ Using: {user['full_name']}" +
        (f"\nStudent ID: {user.get('student_id')}" if user.get('student_id') else "") +
        "\n\nPlease type your message to the psychologist:"
    )
    await callback.message.answer(
        "Type your messages below.\n"
        "When done, click '✅ Done Chatting'",
        reply_markup=chat_session_keyboard()
    )
    await state.set_state(StudentStates.in_chat_session)
    await callback.answer()


@router.callback_query(F.data == "enter_new_credentials", StateFilter(StudentStates.choosing_credentials))
async def enter_new_credentials(callback: CallbackQuery, state: FSMContext):
    """Enter new credentials"""
    await callback.message.edit_text(
        "👤 <b>Share Information</b>\n\n"
        "Please enter your <b>full name</b>:"
    )
    await callback.message.answer(
        "Enter your full name:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(StudentStates.entering_full_name)
    await callback.answer()


@router.message(StateFilter(StudentStates.entering_full_name))
async def process_full_name(message: Message, state: FSMContext):
    """Process full name for identified chat"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    await state.update_data(full_name=message.text)
    await message.answer(
        "Please enter your <b>student ID</b> (optional):\n\n"
        "Click '⏭️ Skip' if you are staff or prefer not to share.",
        reply_markup=skip_keyboard()
    )
    await state.set_state(StudentStates.entering_student_id)


@router.message(StateFilter(StudentStates.entering_student_id))
async def process_student_id(message: Message, state: FSMContext):
    """Process student ID for identified chat (optional)"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    # Allow skipping student ID
    student_id = None if message.text == "⏭️ Skip" else message.text
    await state.update_data(student_id=student_id)
    data = await state.get_data()

    # Save user info to database
    await db.update_user_info(message.from_user.id, data['full_name'], student_id)

    await message.answer(
        f"Thank you, {data['full_name']}!\n\n"
        "Type your messages below.\n"
        "When done, click '✅ Done Chatting'",
        reply_markup=chat_session_keyboard()
    )
    await state.set_state(StudentStates.in_chat_session)


# Continuous chat session handler
@router.message(F.text == "✅ Done Chatting", StateFilter(StudentStates.in_chat_session))
async def done_chatting(message: Message, state: FSMContext):
    """End chat session"""
    await message.answer(
        "✅ Chat session ended.\n\n"
        "Thank you for using our service!",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()
    await state.set_state(StudentStates.choosing_service)


@router.message(F.text == "🔙 Back to Menu", StateFilter(StudentStates.in_chat_session))
async def back_from_chat(message: Message, state: FSMContext):
    """Go back to menu from chat"""
    await cmd_menu(message, state)


@router.message(StateFilter(StudentStates.in_chat_session))
async def process_chat_message(message: Message, state: FSMContext):
    """Process messages in continuous chat session"""
    data = await state.get_data()
    is_anonymous = data.get('is_anonymous', False)

    # Save message to database with student's message_id
    saved_message = await db.save_message(
        message.from_user.id,
        message.text,
        is_anonymous,
        message.message_id
    )

    # Notify psychologist with clean format
    if is_anonymous:
        notification = message.text
    else:
        student_id = data.get('student_id')
        if student_id:
            notification = (
                f"<blockquote>From: {data.get('full_name', 'N/A')}\n"
                f"Student ID: {student_id}</blockquote>\n\n"
                f"{message.text}"
            )
        else:
            notification = (
                f"<blockquote>From: {data.get('full_name', 'N/A')}</blockquote>\n\n"
                f"{message.text}"
            )

    try:
        sent_msg = await message.bot.send_message(PSYCHOLOGIST_ID, notification)
        # Store telegram message ID for reply detection
        await db.update_telegram_message_id(saved_message['id'], sent_msg.message_id)

        # Quick confirmation (no exit from state)
        await message.answer("✅ Sent!")
    except Exception as e:
        print(f"Error sending to psychologist: {e}")
        await message.answer("❌ Error sending message. Please try again.")


# APPOINTMENT BOOKING FLOW
@router.message(F.text == "📅 Book Appointment", StateFilter(StudentStates.choosing_service))
async def book_appointment(message: Message, state: FSMContext):
    """Handle appointment booking"""
    await message.answer(
        "📅 <b>Book an Appointment</b>\n\n"
        "Let's schedule your appointment with the psychologist.\n\n"
        "Please enter your <b>full name</b>:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentStates.entering_appointment_full_name)


@router.message(StateFilter(StudentStates.entering_appointment_full_name))
async def process_appointment_name(message: Message, state: FSMContext):
    """Process full name for appointment"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    await state.update_data(appointment_full_name=message.text)
    await message.answer(
        "Please enter your <b>student ID</b>:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentStates.entering_appointment_student_id)


@router.message(StateFilter(StudentStates.entering_appointment_student_id))
async def process_appointment_student_id(message: Message, state: FSMContext):
    """Process student ID for appointment"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    await state.update_data(appointment_student_id=message.text)

    working_hours = validators.format_working_hours()
    await message.answer(
        f"{working_hours}\n\n"
        "Please enter your <b>preferred date</b>\n"
        "Examples: Monday, 15.10.2024, 15/10/2024",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentStates.entering_preferred_date)


@router.message(StateFilter(StudentStates.entering_preferred_date))
async def process_preferred_date(message: Message, state: FSMContext):
    """Process preferred date"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    await state.update_data(preferred_date=message.text)
    await message.answer(
        "Please enter your <b>preferred time</b> (e.g., 10:00 AM or 14:00):",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentStates.entering_preferred_time)


@router.message(StateFilter(StudentStates.entering_preferred_time))
async def process_preferred_time(message: Message, state: FSMContext):
    """Process preferred time with validation"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    data = await state.get_data()
    preferred_date = data.get('preferred_date')

    # Validate date and time
    is_valid, validation_msg = validators.validate_appointment_time(preferred_date, message.text)

    if not is_valid:
        await message.answer(
            f"{validation_msg}\n\n"
            "Please enter a valid time (e.g., 10:00, 14:30, 2:00 PM):",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
        return

    await state.update_data(preferred_time=message.text)
    await message.answer(
        "✅ Time slot is available!\n\n"
        "Please briefly describe the <b>reason for your appointment</b> (optional):\n\n"
        "Or type 'skip' to skip this step.",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(StudentStates.entering_reason)


@router.message(StateFilter(StudentStates.entering_reason))
async def process_reason(message: Message, state: FSMContext):
    """Process reason and create appointment"""
    if message.text == "❌ Cancel":
        await cmd_menu(message, state)
        return

    reason = message.text if message.text.lower() != 'skip' else "Not specified"
    data = await state.get_data()

    # Create appointment
    appointment = await db.create_appointment(
        message.from_user.id,
        data['appointment_full_name'],
        data['appointment_student_id'],
        data['preferred_date'],
        data['preferred_time'],
        reason
    )

    # Notify psychologist
    notification = (
        f"📅 <b>New Appointment Request</b>\n"
        f"Appointment ID: {appointment['id']}\n\n"
        f"👤 Name: {appointment['full_name']}\n"
        f"🆔 Student ID: {appointment['student_id']}\n"
        f"📆 Preferred Date: {appointment['preferred_date']}\n"
        f"🕐 Preferred Time: {appointment['preferred_time']}\n"
        f"📝 Reason: {appointment['reason']}\n\n"
        f"Manage: /appointments"
    )

    try:
        await message.bot.send_message(PSYCHOLOGIST_ID, notification, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending to psychologist: {e}")

    # Confirm to student
    await message.answer(
        "✅ <b>Appointment Request Sent!</b>\n\n"
        f"📆 Date: {data['preferred_date']}\n"
        f"🕐 Time: {data['preferred_time']}\n\n"
        "The psychologist will review your request and confirm the appointment.\n"
        "You will be notified once it's confirmed.",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()
    await state.set_state(StudentStates.choosing_service)


# ABOUT
@router.message(F.text == "ℹ️ About", StateFilter(StudentStates.choosing_service))
async def show_about(message: Message):
    """Show information about the service"""
    about_text = (
        "ℹ️ <b>About This Service</b>\n\n"
        "This bot connects students of New Uzbekistan University with our professional psychologist.\n\n"
        "<b>Services Available:</b>\n"
        "• Anonymous or identified online counseling\n"
        "• Appointment booking for face-to-face sessions\n"
        "• Confidential and professional support\n\n"
        "<b>Privacy:</b>\n"
        "All communications are confidential. When using anonymous chat, "
        "your identity is protected.\n\n"
        "<b>Response Time:</b>\n"
        "The psychologist typically responds within 24 hours during working days."
    )
    await message.answer(about_text, parse_mode="HTML")


@router.message(F.text == "🔙 Back to Menu")
async def back_to_menu(message: Message, state: FSMContext):
    """Handle back to menu"""
    await cmd_menu(message, state)
