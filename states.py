from aiogram.fsm.state import State, StatesGroup


class StudentStates(StatesGroup):
    choosing_service = State()

    # Chat states
    choosing_chat_type = State()
    entering_full_name = State()
    entering_student_id = State()
    entering_message = State()

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
