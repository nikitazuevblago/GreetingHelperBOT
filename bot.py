from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
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
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))


class Form(StatesGroup):
    tg_credentials = State()
    holiday_name = State()
    holiday_date = State()
    holiday_users = State()
    holiday_text = State()


# Bot commands setup
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="add_holiday", description="Add a new holiday"),
        BotCommand(command="remove_holiday", description="Remove a holiday"),
        BotCommand(command="cancel", description="Cancel the current process"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set successfully.")


@dp.message(Command("cancel"))
async def cancel_process(message: Message, state: FSMContext):
    if await state.get_state():  # Check if the user is in a state
        await state.clear()  # Clear the FSM state
        await message.reply("❌ <b>Process canceled!</b>", parse_mode="HTML")
    else:
        await message.reply("ℹ️ No active process to cancel.", parse_mode="HTML")



# Handler for /start command
@dp.message(CommandStart())
async def start(message: Message) -> None:
    logger.info(f"User triggered /start command.")
    msg = textwrap.dedent((
        "🎉 Hi there! I’m your friendly bot 🤖, here to make your life easier by "
        "sending heartfelt holiday greetings directly from your account. Let me "
        "help you spread joy and celebrate all the special moments! 🥳🎁"))
    await message.reply(msg)


# Start the /add_holiday process
@dp.message(Command("add_holiday"))
async def add_holiday_start(message: Message, state: FSMContext):
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
    invalid_users = [
        user for user in greeted_users if not user.startswith("@")]

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
        add_holiday_DB(holiday_name, day, month,
                       greeted_users, holiday_text)
    except Exception as e:
        logger.error(f"An error occurred while adding holiday: {e}")
        await message.reply("❌ An error occurred while adding the holiday. Please try again later.")
        await state.clear()
        return

    logger.info(
        f"New holiday registered: {holiday_name} on {holiday_date} with message: {holiday_text} for users: {greeted_users}")
    await message.reply(
        f"✅ <b>New holiday registered!</b>\n\n"
        f"🎉 <b>Holiday Name:</b> {holiday_name}\n"
        f"📅 <b>Date:</b> {holiday_date}\n"
        f"📝 <b>Message:</b> {holiday_text}\n"
        f"👥 <b>Users to greet:</b> {', '.join(greeted_users)}",
        parse_mode="HTML"
    )
    await state.clear()


async def send_holiday_greetings():
    while True:
        try:
            # Get the current time and calculate the next 10:00 AM
            now = datetime.now()
            if not os.getenv("IS_TEST"):
                target_time = datetime.combine(now.date(), time(10, 0))
            else:
                target_time = now + timedelta(seconds=30)

            # If it's already past 10:00 AM, target the next day
            if now >= target_time:
                target_time += timedelta(days=1)

            # Calculate the time difference and wait until 10:00 AM
            wait_time = (target_time - now).total_seconds()
            logger.info(
                f"Waiting {wait_time // 60:.2f} minutes until 10:00 AM.")
            await asyncio.sleep(wait_time)

            # Fetch holidays scheduled for today
            today_dd_mm = target_time.strftime("%d-%m")

            # fetch holidays for the current date
            try:
                holidays = fetch_holidays_by_date_DB(today_dd_mm)
            except Exception as e:
                logger.error(f"Error fetching holidays for {today_dd_mm}: {e}")
                holidays = []

            if holidays:
                for holiday in holidays:
                    holiday_name = holiday['name']
                    holiday_message = holiday['message']
                    greeted_users = holiday['greeted_users']

                    for username in greeted_users:
                        try:
                            user = user_account.UserPyrogram(
                                os.getenv("TELEGRAM_ID"))
                            await user.send_msg(username, holiday_message)
                        except Exception as e:
                            logger.error(
                                f"An error occurred while sending holiday message to {username}: {e}")
                            continue

                    logger.info(
                        f"Sent holiday message for {holiday_name} to {greeted_users}")

        except Exception as e:
            logger.error(
                f"An error occurred in the holiday greeting task: {e}")
            # Avoid immediate retry to prevent rapid failure loops
            await asyncio.sleep(60)


@dp.message(Command("remove_holiday"))
async def remove_holiday_command(message: Message):
    holidays = fetch_all_holidays_DB()  # Fetch holidays from the database
    if not holidays:
        await message.answer("No holidays found.")
        return

    # Create an inline keyboard with holiday IDs in callback data
    builder = InlineKeyboardBuilder()
    for holiday in holidays:
        builder.button(
            text=f"❌ {holiday['name']} ({holiday['day']}/{holiday['month']})",
            callback_data=f"toggle_holiday:{holiday['id']}"  # Use holiday ID
        )
    builder.button(text="✅ Confirm Deletion", callback_data="confirm_deletion")
    builder.adjust(1)  # One button per row

    # Attach a temporary storage attribute to the message for selections
    await message.answer(
        "Select the holidays you want to remove (toggle with buttons):",
        reply_markup=builder.as_markup()
    )


@dp.callback_query()
async def handle_holiday_deletion(callback: CallbackQuery):
    if callback.data.startswith("toggle_holiday:"):
        # Extract holiday ID from callback data
        holiday_id = int(callback.data.split(":")[1])

        # Fetch holidays to rebuild the state
        holidays = fetch_all_holidays_DB()

        # Reconstruct the current selection based on IDs in the button text
        selected_ids = set()
        for button in callback.message.reply_markup.inline_keyboard:
            if button[0].text.startswith("✅"):
                selected_ids.add(int(button[0].callback_data.split(":")[1]))

        # Toggle the current holiday's selection state
        if holiday_id in selected_ids:
            selected_ids.remove(holiday_id)
        else:
            selected_ids.add(holiday_id)

        # Build the updated inline keyboard
        builder = InlineKeyboardBuilder()
        for holiday in holidays:
            is_selected = holiday['id'] in selected_ids
            prefix = "✅" if is_selected else "❌"
            builder.button(
                text=f"{prefix} {holiday['name']} ({holiday['day']}/{holiday['month']})",
                callback_data=f"toggle_holiday:{holiday['id']}"
            )
        builder.button(
            text="✅ Confirm Deletion",
            callback_data=f"confirm_deletion:{','.join(map(str, selected_ids))}"
        )
        builder.adjust(1)

        # Update the reply markup
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer(f"Toggled holiday selection.")

    elif callback.data.startswith("confirm_deletion:"):
        # Extract selected IDs from callback data
        selected_ids = callback.data[len("confirm_deletion:"):].split(",")
        selected_ids = list(map(int, selected_ids)) if selected_ids != [""] else []

        if not selected_ids:
            await callback.answer("No holidays selected to delete.")
            return

        # Perform deletion for each selected holiday
        for holiday_id in selected_ids:
            remove_holiday_DB(holiday_id)

        await callback.message.edit_text(
            f"Successfully removed the selected holidays: {', '.join(map(str, selected_ids))}"
        )
        await callback.answer("Holidays removed.")


# Main function
async def main() -> None:
    await set_bot_commands(bot)
    logger.info("Bot polling started.")
    asyncio.create_task(send_holiday_greetings())
    logger.info("Holiday greeting task started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    is_test = int(os.getenv("IS_TEST"))
    print(f"Test state {is_test}")
    if is_test:
        # Drop and recreate tables in test mode
        drop_tables_DB()
        create_tables_DB()

        # Add a test holiday for today
        today = datetime.now().strftime("%d-%m")
        day, month = map(int, today.split("-"))
        add_holiday_DB("Test Holiday",
                       day, month, ['@TrackFoodExpensesBot'],
                       "How you been?")
        add_holiday_DB("Test TESTfasdfadf",
                       day, month, ['@JKUClassNotifierBOT'],
                       "Damn bro, whassup?")
        add_holiday_DB("afdaff",
                       day, month, ['@JKUClassNotifierBOT'],
                       "Damn bro, whassup?")

        logger.info("Test mode enabled. Dropping and recreating tables.")

    logger.info("Starting bot...")
    asyncio.run(main())
