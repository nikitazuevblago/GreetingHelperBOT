import os
from pyrogram import Client
import asyncio


# Define the async function to send a message
async def send_hello(user_id, message, app):
    await app.send_message(chat_id=user_id, text=message)

# Main coroutine to run the application
async def main(user_id, message, api_id, api_hash):
    # Initialize the Pyrogram client
    app = Client("my_account",
                api_id=int(api_id),
                api_hash=api_hash)
    async with app:  # Start the Pyrogram client
        await send_hello(user_id, message, app)  # Replace with the actual user ID or username

# Run the event loop
if __name__ == "__main__":
    api_id=int(os.getenv("API_ID"))
    api_hash=os.getenv("API_HASH")
    asyncio.get_event_loop()\
        .run_until_complete(main("@BotFather", "Hello!", api_id, api_hash))
