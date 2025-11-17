import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, PSYCHOLOGIST_ID
import database as db
from handlers import student, psychologist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to run the bot"""
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Initialize database
    logger.info("Initializing database...")
    await db.init_db()
    logger.info("Database initialized successfully")

    # Register routers
    # Psychologist router should be registered first to handle psychologist-specific commands
    dp.include_router(psychologist.router)
    dp.include_router(student.router)

    logger.info(f"Bot starting... Psychologist ID: {PSYCHOLOGIST_ID}")

    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await db.close_db()
        logger.info("Database connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
