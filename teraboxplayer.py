import os
import re
import logging
import requests,json,logging
import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from pymongo import MongoClient
import threading
from flask import Flask
from threading import Thread
from datetime import timedelta
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_USER_ID= [8025763606,6897739611]


BOT_TOKEN = "7691950524:AAHEvv3hS-nRwNVU7l6zw1zeoBoCkJO3iWk" # Store in environment variables
API_URL = "https://terabox-player-apmf.onrender.com/generate"  # Provide the API URL to generate the streaming link

api_id = "26222466"  
api_hash = "9f70e2ce80e3676b56265d4510561aef" 
notification= -1002167582656

MONGO_URI = "mongodb+srv://botplays90:botplays90@botplays.ycka9.mongodb.net/?retryWrites=true&w=majority&appName=botplays"
DB_NAME = "terabox_bot"
COLLECTION_NAME = "user_ids"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def load_user_ids():
    try:
        # Fetch all user IDs from the database
        user_ids = [user["user_id"] for user in collection.find({}, {"_id": 0, "user_id": 1})]
        return user_ids
    except Exception as e:
        logger.error(f"Error loading user IDs from MongoDB: {e}")
        return []

def save_user_id(user_id):
    try:
        # Check if user_id already exists
        if collection.count_documents({"user_id": user_id}) == 0:
            collection.insert_one({"user_id": user_id})
            logger.info(f"User ID {user_id} saved to the database.")
        else:
            logger.info(f"User ID {user_id} already exists in the database.")
    except Exception as e:
        logger.error(f"Error saving user ID to MongoDB: {e}")



app = Flask('')
@app.route('/')
def home():
    return "I am alive"

def run_http_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http_server)
    os.system("cls")

    t.start()

# Initialize Telegram client
client = TelegramClient('bot',api_id=api_id,api_hash=api_hash).start(bot_token="7921321219:AAGqhOX3S93xADq11Lxvl0zo84kvD72c1Yw")

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.info("Bot is running...")

# Regex pattern to validate TeraBox & TeraShare URLs
VALID_URL_PATTERN = r"https?://(1024terabox|teraboxapp|terabox|terafileshareapp|terafileshare|teraboxlink|terasharelink)\.com/\S+"

# Store the bot's start time
START_TIME = time.time()

# Start command
@client.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):

    # Get user information
    user_id = event.sender_id
    username = event.sender.username
    name=event.sender.first_name
    save_user_id(user_id)

    # Notification message for the channel
    notify_message = (
        f"<b>📢 New user started the terabox!</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Username:</b> @{username}\n\n"
    )

    # Send the notification to a channel (use your notify channel ID or username)
    notify_channel = notification  # Replace this with the actual channel username or ID
    await client.send_message(notify_channel, notify_message, parse_mode="html")

    # Welcome message to the user

    welcome_text = (
        f"✨ Hey **{name}**\n"
        f"👤**User-Id= `{user_id}`\n\n"
        "Welcome to the **TeraBox & TeraShare Stream Bot** 🎬💖\n\n"
        "Ready for an unforgettable streaming experience? 🚀💥\n\n"
        "Simply send me any **TeraBox** or **TeraShare** video link, and I'll instantly generate a **direct streaming link** for you! 🎥💨\n\n"
        "Need any help or just want to say hi? Feel free to reach out to the bot's owner or join our community!\n\n"
        " Send Your terabox Link**! \n\n"
        "Click the buttons below to connect with us! 😊👇"
    )

    buttons = [
        [Button.url("Owner🗿", "https://t.me/botplays90"),
        Button.url("Channel 😁", "https://t.me/join_hyponet")],
        [Button.inline("Send Link ❇️", b"send_link")]  # Inline button to trigger message asking for link
    ]

    # Send the message with the buttons
    await event.respond(welcome_text, parse_mode="markdown", buttons=buttons)

@client.on(events.CallbackQuery(data=b"send_link"))
async def send_link_request(event):
    await event.answer()  # Acknowledge the button click
    await event.respond("❗Please send your **TeraBox** or **TeraShare** video link here! 🚀🎥")


@client.on(events.NewMessage(pattern='/users'))
async def send_user_ids(event):
    if event.sender_id not in ADMIN_USER_ID:
        return  # Only allow the admin to execute this command

    user_ids = load_user_ids()
    total_users = len(user_ids)
    user_list = "\n".join([f"{i + 1}) {user_id}" for i, user_id in enumerate(user_ids)])
    
    # Send total number of users and the list of user IDs
    message = f"Total Users: {total_users}\n\n" + user_list
    await event.respond(message)

# /broad command to send a broadcast message to all users
@client.on(events.NewMessage(pattern='/broad'))
async def broadcast_message(event):
    if event.sender_id not in ADMIN_USER_ID:
        return  # Only allow the admin to execute this command

    # The message to broadcast comes after the /broad command
    message_to_broadcast = event.text[7:].strip()
    if not message_to_broadcast:
        await event.respond("❌ Please provide a message to broadcast.")
        return

    user_ids = load_user_ids()
    success_count = 0
    fail_count = 0
    failed_users = []

    for user_id in user_ids:
        try:
            await client.send_message(user_id, message_to_broadcast)
            success_count += 1
        except Exception as e:
            fail_count += 1
            failed_users.append(user_id)
            logger.error(f"Failed to send message to {user_id}: {e}")

    # Prepare summary message
    summary_message = (
        f"🌐 Broadcast Summary of terabox bot:\n"
        f"❇️ Sent successfully to {success_count} users.\n"
        f"❌ Failed to send to {fail_count} users.\n"
        f"Blocked users or errors: {len(failed_users)}\n"
    )

    # Send the summary to the admin
    await event.respond(summary_message)


@client.on(events.NewMessage())
async def handle_random_message(event):
    message_text = event.text

    # Check if the message starts with a command (i.e., starts with "/")
    if message_text.startswith("/"):
        return

    # Check if the message is sent from a channel or group
    if event.is_channel or event.is_group:
        # If the message comes from a channel or group, do not respond
        return

    # Check if the message matches the valid TeraBox URL pattern
    if not re.match(VALID_URL_PATTERN, message_text):
        # If not a valid TeraBox URL, ask the user to send a valid one
        await event.respond("❌ Please enter a valid **TeraBox or TeraShare video link**. 🚫")



@client.on(events.NewMessage())
async def handle_message(event):
    # Extract the message content (text) from the user
    message_text = event.raw_text
    
    # Check if the message matches the valid URL pattern
    if re.match(VALID_URL_PATTERN, message_text):
        # Extract user details
        user_id = event.sender_id
        username = event.sender.username if event.sender.username else "N/A"
        first_name = event.sender.first_name if event.sender.first_name else "N/A"
        
        # Prepare the message to be sent to the channel
        user_details = (
            f"📤 **User Information**:\n"
            f"🆔 **User ID**: `{user_id}`\n"
            f"👤 **Username**: @{username}\n"
            f"👤 **Name**: {first_name}\n\n"
        )
        
        # Prepare the message with the valid link
        message = f"\n------------------------------------------------\n✅ **TeraBox link received**:\n\n{user_details}\n{message_text}\n------------------------------------------------"
        
        # Send the message to the specified channel
        await client.send_message(notification, message)
        



@client.on(events.NewMessage(pattern='/uptime'))
async def send_uptime(event):
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = str(timedelta(seconds=uptime_seconds))  # Convert seconds to readable format
    await event.respond(f"⏳ **Bot Uptime:** `{uptime_str}`", parse_mode="Markdown")

async def process_video(chat_id, video_url):
    try:
        # Check if the video_url matches the VALID_URL_PATTERN
        if not re.match(VALID_URL_PATTERN, video_url):
            await client.send_message(chat_id, "❌ Please send a valid **TeraBox or TeraShare video link**.")
            return
        
        # Notify user and get message ID
        processing_message = await client.send_message(chat_id, "⏳ Processing your video link... Please wait. 🚀")

        # API request
        response = requests.post(API_URL, json={"video_url": video_url}, timeout=15)
        response.raise_for_status()  # Raises an error for non-200 status codes
        
        data = response.json()

        # Delete the processing message before sending the result
        await client.delete_messages(chat_id, processing_message.id)

        if "stream_link" in data:
            stream_link = data["stream_link"]

            # Create inline keyboard buttons using Button.inline
            buttons = [
                [Button.url("Owner🗿", "https://t.me/botplays90"),
                 Button.url("Channel 😁", "https://t.me/join_hyponet")],
                [Button.url("🎥 Watch Online", stream_link)]
            ]

            # Send streaming link with buttons
            await client.send_message(chat_id, "✅ Your streaming link is ready! Click below to watch 🎬", buttons=buttons)

        else:
            await client.send_message(chat_id, f"❌ Error: {data.get('error', 'Failed to generate the stream link.')}")

    except requests.exceptions.Timeout:
        await client.send_message(chat_id, "⚠️ The request timed out. Please try again later.")
    
    except requests.exceptions.RequestException as e:
        await client.send_message(chat_id, f"⚠️ API Error: {str(e)}")
    
    except Exception as e:
        await client.send_message(chat_id, f"⚠️ An unexpected error occurred: {str(e)}")


@client.on(events.NewMessage())
async def handle_message(event):
    video_url = event.text
    chat_id = event.chat_id
    if re.match(VALID_URL_PATTERN, video_url):
        # Run video processing in a separate thread to not block the main loop
        asyncio.create_task(process_video(chat_id, video_url))

# Run Flask server for keeping bot alive
if __name__ == "__main__":
    keep_alive()
    logging.info("Starting bot polling...")

    # Start the bot using asyncio loop
    client.start()
    client.run_until_disconnected()
