import argparse
from telegram import Bot
import logging
import os
import dotenv

import asyncio

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Send an image to a Telegram chat with an optional caption.')
parser.add_argument('img_path', type=str, help='Path to the picture to send (required)')
parser.add_argument('env_path', type=str, help='Path to the file with tokens (required)')
parser.add_argument('--caption', type=str, default='Check out this picture!', help='Caption for the picture (optional)')

args = parser.parse_args()

# Load environment variables
dotenv.load_dotenv(args.env_path)

bot_token = os.environ["TG_bot_token"]
channel_id = '@zoo_highlights'

# Create a bot instance
bot = Bot(token=bot_token)


async def main():
    # Send a picture with the provided or default caption
    image_path = args.img_path
    image_caption = args.caption
    await bot.send_photo(chat_id=channel_id, photo=open(image_path, 'rb'), caption=image_caption)
    # await bot.send_document(chat_id=channel_id, document=open(image_path, "rb"), caption=image_caption) # without compression



if __name__ == "__main__":
    # Run the event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
