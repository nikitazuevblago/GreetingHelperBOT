import os
import asyncio
from pyrogram import Client
from custom_logging import logger


class UserPyrogram:
    def __init__(self, user_id):
        # Load API credentials from environment variables
        api_id = int(os.getenv("API_ID"))
        api_hash = os.getenv("API_HASH")

        # Ensure sessions directory exists
        os.makedirs("sessions", exist_ok=True)
        session_name = f"sessions/{user_id}"

        # Initialize the Pyrogram client
        self.app = Client(
            session_name,  # Use forward slashes for cross-platform compatibility
            api_id=int(api_id),
            api_hash=api_hash
        )

    async def send_msg(self, receiver_id, message):
        """Send a message to a receiver."""
        async with self.app:
            try:
                await self.app.send_message(receiver_id, message)
                logger.info(f"Message sent to {receiver_id}: {message}")
            except Exception as error:
                logger.error(
                    f"An error occurred while sending the message: {error}")


if __name__ == "__main__":
    # Specify the recipient and the message
    user_id = 5303965494
    message = "Hello, World!"
    receiver_id = "@BotFather"

    # Create a User instance
    user = UserPyrogram(user_id)

    # Use the existing event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(user.send_msg(receiver_id, message))
