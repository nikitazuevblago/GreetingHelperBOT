import os
import asyncio
from pyrogram import Client
from db_interaction import get_all_users_DB
from custom_logging import logger


class UserPyrogram:
    def __init__(self, api_id, api_hash, user_id, create_new_session=True):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = None
        self.phone_code = None
        self.password = None

        # Ensure sessions directory exists
        os.makedirs("sessions", exist_ok=True)
        session_name = f"sessions/{user_id}"

        # os.remove(session_name+'.session') \
        #     if os.path.exists(session_name+'.session') and create_new_session else None

        # Initialize the Pyrogram client
        self.app = Client(
            session_name,  # Use forward slashes for cross-platform compatibility
            api_id=int(api_id),
            api_hash=api_hash
        )
    
    # Method to request a login code (placeholder for further implementation)
    async def request_code(self, phone_number):
        self.app.phone_number = phone_number
        await self.app.connect()
        logger.info(f"Requesting OTP code for phone number: {phone_number}")
        await self.app.send_code(phone_number)
        await self.app.disconnect()
        logger.info("Code OTP requested. Disconnected.")
    
    # Method to enter the received code 
    async def enter_code(self, phone_code):
        logger.info(f"Entering OTP code: {phone_code}")
        self.app.phone_code = phone_code

    async def send_msg(self, receiver_id, message):
        async with self.app:
            await self.app.send_message(chat_id=receiver_id, text=message)
            logger.info(f"Message sent to user: {receiver_id}")


if __name__ == "__main__":
    # Load API credentials from environment variables
    api_id = int(os.getenv("API_ID")) 
    api_hash = os.getenv("API_HASH")  

    # Specify the recipient and the message
    user_id = 5303965494
    message = "Why are you running?"
    receiver_id = "@BotFather"

    # Create a User instance
    user = UserPyrogram(api_id, api_hash, user_id, create_new_session=False)

    # Use the existing event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(user.send_msg(receiver_id, message))