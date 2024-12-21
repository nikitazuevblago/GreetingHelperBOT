from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendPoll
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, time
import asyncio
import os
import textwrap
from db_interaction import *
from custom_logging import logger
import user_account


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize dispatcher and bot
dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

class Form(StatesGroup):
    tg_credentials = State()
    holiday_name = State()
    holiday_date = State()
    holiday_users = State()
    holiday_text = State()
    phone_number = State()
    otp_code = State()


# Bot commands setup
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="register", description="Register account for sending greetings"),
        BotCommand(command="add_holiday", description="Add a new holiday"),
        BotCommand(command="cancel", description="Cancel the current process"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set successfully.")


# Handler for /start command
@dp.message(CommandStart())
async def start(message: Message) -> None:
    logger.info(f"User {message.from_user.id} triggered /start command.")
    msg = textwrap.dedent((
    "🎉 Hi there! I’m your friendly bot 🤖, here to make your life easier by "
    "sending heartfelt holiday greetings directly from your account. Let me "
    "help you spread joy and celebrate all the special moments! 🥳🎁"))
    await message.reply(msg)







@dp.message(Command("register"))
async def register(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} triggered /register command.")
    msg = textwrap.dedent((
    "🚀 Hi there! To enable me to send messages from your account, I need your <b>API ID</b> and <b>API hash</b>. "
    "Here's how you can get them:\n\n"
    "1️⃣ <b>Log in</b> to your Telegram core: <a href='https://my.telegram.org'>Telegram Core</a>.\n"
    "2️⃣ Navigate to <b>API development tools</b> and fill out the form.\n"
    "3️⃣ Once completed, you will receive:\n"
    "   - 🛠️ <b>API ID</b>\n"
    "   - 🔑 <b>API Hash</b>\n\n"
    "📥 <b>Please send me the credentials</b> in this format:\n"
    "<b>API_ID API_HASH</b> (separated by a space).\n\n"
    ))
    await message.reply(msg)
    await state.set_state(Form.tg_credentials)


@dp.message(Form.tg_credentials)
async def request_phone_number(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent tg_credentials")
    try:
        api_id, api_hash = message.text.split()
        api_id = int(api_id)
        await state.update_data(api_id=api_id, api_hash=api_hash)
        await message.reply("Great! Now, please send me your phone number (with country code, e.g., +123456789).")
        await state.set_state(Form.phone_number)
    except Exception as e:
        logger.error(f"User {message.from_user.id} entered invalid credentials. {e}")
        await message.reply("Try again, use space as separator and enter API_ID as number!")
        await state.set_state(Form.tg_credentials)


@dp.message(Form.phone_number)
async def request_otp(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent phone number")
    try:
        phone_number = message.text
        await state.update_data(phone_number=phone_number)
        await message.reply("Thanks! Now, please send the OTP code you received.")
        await state.set_state(Form.otp_code)
    except Exception as e:
        logger.error(f"Error while receiving phone number from User {message.from_user.id}. {e}")
        await message.reply("Invalid phone number format. Please try again!")
        await state.set_state(Form.phone_number)


@dp.message(Form.otp_code)
async def register_user(message: Message, state: FSMContext) -> None:
    logger.info(f"User {message.from_user.id} sent OTP code")
    try:
        otp_code = message.text
        data = await state.get_data()
        api_id = data.get("api_id")
        api_hash = data.get("api_hash")
        phone_number = data.get("phone_number")
        
        # Check if the user already exists
        users_rows = get_all_users_DB()
        registered_tg_ids = [row[1] for row in users_rows]
        if message.from_user.id in registered_tg_ids:
            logger.info(f"User {message.from_user.id} is being re-registered.")
            remove_user_DB(message.from_user.id)
        
        # Save user data in DB
        add_user_DB(message.from_user.id, api_id, api_hash, phone_number)
        logger.info(f"User {message.from_user.id} registered successfully.")
        await message.reply(
            "You have been registered successfully! "
            "As a test, 'Hello!' will be sent to @BotFather from your account. "
            "If the message hasn't been sent, "
            "please check your credentials and try registering again."
        )
        # Send a test message to @BotFather
        try:
            await user_account.main("@BotFather", "Hello!", api_id, api_hash)
        except Exception as e:
            logger.error(f"An error occurred while sending a test message to @BotFather: {e}")
            await message.reply("An error occurred while sending a test message to @BotFather. Please try again later.")

        # Reset the state after successful registration
        await state.clear()
    except Exception as e:
        logger.error(f"User {message.from_user.id} encountered an error. {e}")
        await message.reply("Something went wrong! Please try again.")
        await state.set_state(Form.tg_credentials)





# Start the /add_holiday process
@dp.message(Command("add_holiday"))
async def add_holiday_start(message: Message, state: FSMContext):
    # Add register check here
    users_rows = get_all_users_DB()
    registered_tg_ids = [row[1] for row in users_rows]
    if message.from_user.id not in registered_tg_ids:
        await message.reply("❌ You need to register your account first with /register.")
        return

    await message.reply(
        "🎉 <b>Let's add a new holiday!</b>\n\n"
        "Please enter the <b>name of the holiday</b> (e.g., International Friendship Day):",
        parse_mode="HTML"
    )
    await state.set_state(Form.holiday_name)

# Get the holiday name
@dp.message(Form.holiday_name)
async def get_holiday_name(message: Message, state: FSMContext):
    await state.update_data(holiday_name=message.text)
    await message.reply(
        "📅 Great! Now enter the <b>date of the holiday</b> in the format <code>DD-MM</code> (e.g., 14-02 for Valentine's Day):",
        parse_mode="HTML"
    )
    await state.set_state(Form.holiday_date)

# Get the holiday date
@dp.message(Form.holiday_date)
async def get_holiday_date(message: Message, state: FSMContext):
    try:
        # Validate the date format
        date_parts = message.text.split("-")
        if len(date_parts) != 2 or not all(part.isdigit() for part in date_parts):
            raise ValueError

        day, month = map(int, date_parts)
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError
    except ValueError:
        await message.reply(
            "❌ Invalid date format! Please enter the date in the format <code>DD-MM</code> (e.g., 14-02 for Valentine's Day):",
            parse_mode="HTML"
        )
        return

    await state.update_data(holiday_date=message.text)
    await message.reply(
        "📝 Now, please enter a <b>custom holiday message</b> to be sent to the users.\n\n"
        "For example: <i>Happy Friendship Day! Wishing you joy and happiness!</i>",
        parse_mode="HTML"
    )
    await state.set_state(Form.holiday_text)

# Get the custom holiday message
@dp.message(Form.holiday_text)
async def get_holiday_text(message: Message, state: FSMContext):
    await state.update_data(holiday_text=message.text)
    await message.reply(
        "👥 Great! Finally, please enter the <b>usernames</b> of the people to greet for this holiday.\n\n"
        "Use the format: <code>@username1 @username2 @username3</code>\n"
        "Separate each username with a space:",
        parse_mode="HTML"
    )
    await state.set_state(Form.holiday_users)

# Get the users to greet and complete the process
@dp.message(Form.holiday_users)
async def get_holiday_users(message: Message, state: FSMContext):
    greeted_users = message.text.split()
    invalid_users = [user for user in greeted_users if not user.startswith("@")]

    if invalid_users:
        await message.reply(
            f"❌ The following usernames are invalid: {', '.join(invalid_users)}\n\n"
            "Make sure all usernames start with <code>@</code> and try again:",
            parse_mode="HTML"
        )
        return

    data = await state.get_data()
    holiday_name = data.get("holiday_name")
    holiday_date = data.get("holiday_date")
    day, month = map(int, holiday_date.split("-"))
    holiday_text = data.get("holiday_text")

    # Register the holiday in the database
    try:
        add_holiday_DB(message.from_user.id, holiday_name, day, month,
                    greeted_users, holiday_text)
    except Exception as e:
        logger.error(f"An error occurred while adding holiday: {e}")
        await message.reply("❌ An error occurred while adding the holiday. Please try again later.")
        await state.clear()
        return

    logger.info(f"New holiday registered: {holiday_name} on {holiday_date} with message: {holiday_text} for users: {greeted_users}")
    await message.reply(
        f"✅ <b>New holiday registered!</b>\n\n"
        f"🎉 <b>Holiday Name:</b> {holiday_name}\n"
        f"📅 <b>Date:</b> {holiday_date}\n"
        f"📝 <b>Message:</b> {holiday_text}\n"
        f"👥 <b>Users to greet:</b> {', '.join(greeted_users)}",
        parse_mode="HTML"
    )
    await state.clear()



# Command to cancel the process
@dp.message(Command("cancel"))
async def cancel_process(message: Message, state: FSMContext):
    await state.clear()  # Clear any ongoing FSM process
    await message.reply("❌ <b>Process canceled!</b> You can start again with /add_holiday.", parse_mode="HTML")



# Main function
async def main() -> None:
    await set_bot_commands(bot)
    logger.info("Bot polling started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    is_test = int(os.getenv("IS_TEST"))
    if is_test:
        # Drop and recreate tables in test mode
        drop_tables_DB()
        create_tables_DB()
        logger.info("Test mode enabled. Dropping and recreating tables.")

    logger.info("Starting bot...")
    asyncio.run(main())