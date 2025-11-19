from aiogram.fsm.state import State, StatesGroup


class StudentStates(StatesGroup):
    choosing_service = State()

    # Chat states
    choosing_chat_type = State()
    choosing_credentials = State()  # Choose between last used or new credentials
    entering_full_name = State()
    entering_student_id = State()
    entering_message = State()
    in_chat_session = State()  # Continuous chat session

    # Appointment states
    entering_appointment_full_name = State()
    entering_appointment_student_id = State()
    entering_preferred_date = State()
    entering_preferred_time = State()
    entering_reason = State()


class PsychologistStates(StatesGroup):
    viewing_messages = State()
    replying_to_message = State()
    managing_appointments = State()
    updating_appointment = State()
    entering_appointment_comment = State()  # For optional comment on actions
