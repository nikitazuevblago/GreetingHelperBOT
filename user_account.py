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

        os.remove(session_name+'.session') \
            if os.path.exists(session_name+'.session') and create_new_session else None

        # Initialize the Pyrogram client
        self.app = Client(
            session_name,  # Use forward slashes for cross-platform compatibility
            api_id=int(api_id),
            api_hash=api_hash
        )
    
    # async def request_code(self, phone_number):
    #     await self.app.connect()
    #     self.phone_number = phone_number
    #     sent_code = await self.app.send_code(phone_number)
    #     self.phone_code_hash = sent_code.phone_code_hash  # Store fresh phone_code_hash
    #     logger.info(f"New code sent to {phone_number}: {sent_code}")
    #     return sent_code



    # async def enter_code(self, phone_code):
    #     try:
    #         await self.app.sign_in(
    #             phone_number=self.phone_number,
    #             phone_code_hash=self.phone_code_hash,
    #             phone_code=phone_code
    #         )
    #         logger.info("Successfully logged in.")
    #     except Exception as e:
    #         logger.error(f"Login failed: {e}")
    #     finally:
    #         await self.app.disconnect()

    async def send_msg(self, receiver_id, message):
        """Send a message to a receiver."""
        if not self.app.is_connected:  # Ensure the client is connected
            await self.app.connect()
        try:
            await self.app.send_message(chat_id=receiver_id, text=message)
            logger.info(f"Message sent to user: {receiver_id}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
        finally:
            await self.app.disconnect()  # Disconnect if you don't need to reuse the session

# if __name__ == "__main__":
#     # Load API credentials from environment variables
#     api_id = int(os.getenv("API_ID")) 
#     api_hash = os.getenv("API_HASH")  

#     # Specify the recipient and the message
#     user_id = 5303965494
#     message = "Why are you running?"
#     receiver_id = "@BotFather"

#     # Create a User instance
#     user = UserPyrogram(api_id, api_hash, user_id, create_new_session=False)

#     # Use the existing event loop
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(user.send_msg(receiver_id, message))