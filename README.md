# University Psychology Support Bot

A Telegram bot for New Uzbekistan University that connects students with a university psychologist.

## Features

### For Students:
- **Online Chat**: Send messages to the psychologist
  - Anonymous chat option
  - Identified chat (with full name and student ID)
- **Appointment Booking**: Schedule face-to-face sessions
- **Confidential Support**: All communications are private and professional

### For Psychologist:
- **Message Management**: View and reply to student messages
- **Appointment Management**: Confirm, cancel, or complete appointments
- **Statistics**: View overview of messages and appointments
- **Message Routing**: Bot automatically routes replies to the correct student

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```
BOT_TOKEN=your_bot_token_from_botfather
PSYCHOLOGIST_ID=telegram_id_of_psychologist
DATABASE_URL=postgresql://user:password@localhost:5432/psy_bot
```

**How to get these values:**
- **BOT_TOKEN**: Create a bot with [@BotFather](https://t.me/botfather) on Telegram
- **PSYCHOLOGIST_ID**:
  1. Use [@userinfobot](https://t.me/userinfobot) on Telegram
  2. Forward a message from the psychologist's account to get their ID
- **DATABASE_URL**: Your PostgreSQL connection string

### 3. Set Up PostgreSQL Database

Make sure PostgreSQL is installed and running, then create a database:

```bash
createdb psy_bot
```

Or using SQL:

```sql
CREATE DATABASE psy_bot;
```

### 4. Run the Bot

```bash
python main.py
```

The bot will automatically create the necessary database tables on first run.

## Usage

### For Students:

1. Start the bot: `/start`
2. Choose an option:
   - **Book Appointment**: Schedule a session with the psychologist
   - **Online Chat**: Send a message (anonymous or identified)

### For Psychologist:

1. Start the bot: `/start`
2. Use the menu to:
   - **View Messages**: See and reply to student messages
   - **Manage Appointments**: Confirm, cancel, or complete appointments
   - **Statistics**: View system statistics

**Quick Commands:**
- `/reply <message_id>` - Quick reply to a specific message
- `/appointments` - Quick access to appointments

## Database Schema

### Tables:
- **users**: Store student information
- **messages**: Store chat messages and replies
- **appointments**: Store appointment requests

## Project Structure

```
psy/
├── main.py                 # Bot entry point
├── config.py              # Configuration and environment variables
├── database.py            # Database models and operations
├── states.py              # FSM states
├── keyboards.py           # Telegram keyboards
├── handlers/
│   ├── __init__.py
│   ├── student.py         # Student interaction handlers
│   └── psychologist.py    # Psychologist interaction handlers
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your environment variables (create this)
└── README.md             # This file
```

## Security Notes

- The `.env` file contains sensitive information and is excluded from git
- Only the configured psychologist can access psychologist features
- Anonymous messages protect student identity
- All database credentials should be kept secure

## Troubleshooting

### Bot doesn't respond:
- Check if BOT_TOKEN is correct
- Verify the bot is running without errors
- Check your internet connection

### Database connection errors:
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists

### Psychologist features not working:
- Verify PSYCHOLOGIST_ID is correct
- The ID must be a number, not a username

## Support

For issues or questions, contact the system administrator.
