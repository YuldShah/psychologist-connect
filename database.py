import asyncpg
from datetime import datetime
from typing import Optional, List
from config import DATABASE_URL

# Global connection pool
pool: Optional[asyncpg.Pool] = None


async def init_db():
    """Initialize database connection pool and create tables"""
    global pool

    # Create connection pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)

    # Create tables
    async with pool.acquire() as conn:
        # Users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                full_name VARCHAR(255),
                student_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Messages table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                message_text TEXT NOT NULL,
                is_anonymous BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                replied BOOLEAN DEFAULT FALSE,
                psychologist_reply TEXT,
                reply_at TIMESTAMP
            )
        ''')

        # Appointments table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                full_name VARCHAR(255) NOT NULL,
                student_id VARCHAR(100) NOT NULL,
                preferred_date VARCHAR(255) NOT NULL,
                preferred_time VARCHAR(255) NOT NULL,
                reason TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        # Create indexes for better performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)
        ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_replied ON messages(replied)
        ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)
        ''')


async def close_db():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()


async def get_or_create_user(telegram_id: int, username: Optional[str] = None) -> dict:
    """Get existing user or create new one"""
    async with pool.acquire() as conn:
        # Try to get existing user
        user = await conn.fetchrow(
            'SELECT * FROM users WHERE telegram_id = $1',
            telegram_id
        )

        if not user:
            # Create new user
            user = await conn.fetchrow(
                '''
                INSERT INTO users (telegram_id, username)
                VALUES ($1, $2)
                RETURNING *
                ''',
                telegram_id, username
            )

        return dict(user) if user else None


async def update_user_info(telegram_id: int, full_name: str, student_id: str):
    """Update user's full name and student ID"""
    async with pool.acquire() as conn:
        await conn.execute(
            '''
            UPDATE users
            SET full_name = $1, student_id = $2
            WHERE telegram_id = $3
            ''',
            full_name, student_id, telegram_id
        )


async def save_message(telegram_id: int, message_text: str, is_anonymous: bool = False) -> Optional[dict]:
    """Save a message from user"""
    async with pool.acquire() as conn:
        # Get user
        user = await conn.fetchrow(
            'SELECT id FROM users WHERE telegram_id = $1',
            telegram_id
        )

        if user:
            # Create message
            message = await conn.fetchrow(
                '''
                INSERT INTO messages (user_id, message_text, is_anonymous)
                VALUES ($1, $2, $3)
                RETURNING *
                ''',
                user['id'], message_text, is_anonymous
            )
            return dict(message) if message else None

        return None


async def get_unreplied_messages() -> List[dict]:
    """Get all unreplied messages for psychologist"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''
            SELECT * FROM messages
            WHERE replied = FALSE
            ORDER BY created_at ASC
            '''
        )
        return [dict(row) for row in rows]


async def get_message_by_id(message_id: int) -> Optional[dict]:
    """Get message by ID"""
    async with pool.acquire() as conn:
        message = await conn.fetchrow(
            'SELECT * FROM messages WHERE id = $1',
            message_id
        )
        return dict(message) if message else None


async def reply_to_message(message_id: int, reply_text: str) -> Optional[dict]:
    """Save psychologist's reply to a message"""
    async with pool.acquire() as conn:
        message = await conn.fetchrow(
            '''
            UPDATE messages
            SET psychologist_reply = $1, replied = TRUE, reply_at = $2
            WHERE id = $3
            RETURNING *
            ''',
            reply_text, datetime.utcnow(), message_id
        )
        return dict(message) if message else None


async def create_appointment(telegram_id: int, full_name: str, student_id: str,
                            preferred_date: str, preferred_time: str, reason: str) -> Optional[dict]:
    """Create a new appointment"""
    async with pool.acquire() as conn:
        # Get user
        user = await conn.fetchrow(
            'SELECT id FROM users WHERE telegram_id = $1',
            telegram_id
        )

        if user:
            # Create appointment
            appointment = await conn.fetchrow(
                '''
                INSERT INTO appointments (user_id, full_name, student_id, preferred_date, preferred_time, reason)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                ''',
                user['id'], full_name, student_id, preferred_date, preferred_time, reason
            )
            return dict(appointment) if appointment else None

        return None


async def get_pending_appointments() -> List[dict]:
    """Get all pending appointments"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''
            SELECT * FROM appointments
            WHERE status = 'pending'
            ORDER BY created_at ASC
            '''
        )
        return [dict(row) for row in rows]


async def get_all_appointments() -> List[dict]:
    """Get all appointments"""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''
            SELECT * FROM appointments
            ORDER BY created_at DESC
            '''
        )
        return [dict(row) for row in rows]


async def update_appointment_status(appointment_id: int, status: str, notes: Optional[str] = None) -> Optional[dict]:
    """Update appointment status"""
    async with pool.acquire() as conn:
        if notes:
            appointment = await conn.fetchrow(
                '''
                UPDATE appointments
                SET status = $1, notes = $2
                WHERE id = $3
                RETURNING *
                ''',
                status, notes, appointment_id
            )
        else:
            appointment = await conn.fetchrow(
                '''
                UPDATE appointments
                SET status = $1
                WHERE id = $2
                RETURNING *
                ''',
                status, appointment_id
            )

        return dict(appointment) if appointment else None


async def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by database ID"""
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            'SELECT * FROM users WHERE id = $1',
            user_id
        )
        return dict(user) if user else None


async def get_appointment_by_id(appointment_id: int) -> Optional[dict]:
    """Get appointment by ID"""
    async with pool.acquire() as conn:
        appointment = await conn.fetchrow(
            'SELECT * FROM appointments WHERE id = $1',
            appointment_id
        )
        return dict(appointment) if appointment else None
