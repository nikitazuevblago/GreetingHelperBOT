import os
import asyncio
from pyrogram import Client
from db_interaction import get_all_users_DB
from custom_logging import logger


class User:
    def __init__(self, api_id, api_hash, user_id, create_new_session=True):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = None
        self.phone_code = None
        self.password = None

        # Ensure sessions directory exists
        os.makedirs("sessions", exist_ok=True)
        session_name = f"sessions/{user_id}"

        os.remove(session_name) \
            if os.path.exists(session_name) and create_new_session else None

        # Initialize the Pyrogram client
        self.app = Client(
            session_name,  # Use forward slashes for cross-platform compatibility
            api_id=int(api_id),
            api_hash=api_hash
        )

    async def send_msg(self, receiver_id, message):
        async with self.app:
            await self.app.send_message(chat_id=receiver_id, text=message)
            logger.info(f"Message sent to user: {user_id}")


if __name__ == "__main__":
    # Load API credentials from environment variables
    api_id = int(os.getenv("API_ID")) 
    api_hash = os.getenv("API_HASH")  

    # Specify the recipient and the message
    user_id = 5303965494
    message = "Why are you running?"
    receiver_id = "@BotFather"

    # Create a User instance
    user = User(api_id, api_hash, user_id, create_new_session=False)

    # Use the existing event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(user.send_msg(receiver_id, message))