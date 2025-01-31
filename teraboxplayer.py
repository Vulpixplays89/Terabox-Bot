import os
import re
import logging
import requests
import telebot
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import timedelta
from flask import Flask
from threading import Thread 

# Load bot token securely
BOT_TOKEN = "7523629650:AAGBOekD0BeS7WvrNA8rN-ar3fb8RSdNRCE"  # Store in environment variables
API_URL = "https://terabox-player-apmf.onrender.com/generate"

app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run_http_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http_server)
    t.start()

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.info("Bot is running...")

# Regex pattern to validate TeraBox & TeraShare URLs
VALID_URL_PATTERN = r"https?://(teraboxlink|terasharelink)\.com/\S+"

# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🌸✨ Hello, dear! ✨🌸\n\n"
        "Welcome to **TeraBox & TeraShare Stream Bot** 🎬💖\n"
        "Just send me a **TeraBox or TeraShare video link**, and I'll generate a **direct streaming link** for you! 🚀🎥\n\n"
        "Enjoy your streaming! 🍿😊"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# Function to process video link in a separate thread
def process_video(chat_id, video_url):
    try:
        # Validate the URL
        if not re.match(VALID_URL_PATTERN, video_url):
            bot.send_message(chat_id, "❌ Please send a valid **TeraBox or TeraShare video link**.")
            return
        
        # Notify user and get message ID
        processing_message = bot.send_message(chat_id, "⏳ Processing your video link... Please wait. 🚀")

        # API request
        response = requests.post(API_URL, json={"video_url": video_url}, timeout=15)
        response.raise_for_status()  # Raises an error for non-200 status codes
        
        data = response.json()

        # Delete the processing message before sending the result
        bot.delete_message(chat_id, processing_message.message_id)

        if "stream_link" in data:
            stream_link = data["stream_link"]

            # Create inline keyboard
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("Owner🗿", url="https://t.me/botplays90"),
                InlineKeyboardButton("Channel 😁", url="https://t.me/join_hyponet")
            )
            markup.row(
                InlineKeyboardButton("🎥 Watch Online", url=stream_link)
            )

            # Send streaming link with buttons
            bot.send_message(chat_id, "✅ Your streaming link is ready! Click below to watch 🎬", reply_markup=markup)

        else:
            bot.send_message(chat_id, f"❌ Error: {data.get('error', 'Failed to generate the stream link.')}")
    
    except requests.exceptions.Timeout:
        bot.send_message(chat_id, "⚠️ The request timed out. Please try again later.")
    
    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id, f"⚠️ API Error: {str(e)}")
    
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ An unexpected error occurred: {str(e)}")
        

# Store the bot's start time
START_TIME = time.time()

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = str(timedelta(seconds=uptime_seconds))  # Convert seconds to readable format
    bot.send_message(message.chat.id, f"⏳ **Bot Uptime:** `{uptime_str}`", parse_mode="Markdown")
    


# Message handler for TeraBox & TeraShare links
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    threading.Thread(target=process_video, args=(message.chat.id, message.text)).start()

# 

if __name__ == "__main__":
    keep_alive()
    
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            time.sleep(5)
            
# Run the bot
logging.info("Starting bot polling...")
bot.infinity_polling()            
