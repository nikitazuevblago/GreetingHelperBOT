from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime, timedelta, time
import asyncio
import os
import traceback
import textwrap
from schedule import *
from db_interaction import *
from custom_logging import logger


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize dispatcher
dp = Dispatcher()

class Form(StatesGroup):
    asking_calendar_url = State()


# Bot commands setup
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot")
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set successfully.")


# Handler for /start command
@dp.message(CommandStart())
async def ask_calendar_url(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} triggered /start command.")
    msg = textwrap.dedent("""\
    🎉 Hi there! I’m your friendly bot 🤖,
    here to make your life easier by sending heartfelt holiday greetings 🎈✨ 
    directly from your account. Let me help you spread joy and celebrate 
    all the special moments! 🥳🎁""")
    await message.reply(msg)
    logger.info(f"Prompted user {message.from_user.id} for calendar URL.")
    await state.set_state(Form.asking_calendar_url)


# # Main function
# async def main() -> None:
#     bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
#     await set_bot_commands(bot)
#     asyncio.create_task(send_daily_schedule(bot))  
#     logger.info("Bot polling started.")
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     is_test = int(os.getenv("IS_TEST"))
#     if is_test:
#         drop_tables_DB()
#         create_tables_DB()
#         logger.info("Test mode enabled. Dropping and recreating tables.")
#         add_mailing_date_DB(get_current_date())
#         logger.info("Test database setup completed.")
#     logger.info("Starting bot...")
#     asyncio.run(main())