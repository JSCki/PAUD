# bot.py

import time
import requests
import json
import threading
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace with your NEW secure bot token (DO NOT share this)
BOT_TOKEN = '8304862459:AAEL1lAv2PJbGYn_VG9KxF0tra9RQQLVeu8'
FIREBASE_URL = 'https://free-7d474-default-rtdb.asia-southeast1.firebasedatabase.app/message.json'

bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

USERS_FILE = 'users.json'
LAST_VERSION_FILE = 'last_version.txt'


# Load users from local file
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


# Save users to local file
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)


# /start command handler
def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        print(f"✅ New user added: {user_id}")
    update.message.reply_text("✅ Bot activated! You'll receive updates automatically.")


dispatcher.add_handler(CommandHandler('start', start))


# Load last sent version
def get_last_version():
    try:
        with open(LAST_VERSION_FILE, 'r') as f:
            return int(f.read())
    except:
        return -1


# Save last sent version
def save_version(version):
    with open(LAST_VERSION_FILE, 'w') as f:
        f.write(str(version))


# Broadcast message to all users
def broadcast(message_data):
    text = message_data.get('text', '')
    buttons = message_data.get('buttons', [])

    # Build button markup
    keyboard = [
        [InlineKeyboardButton(btn['text'], url=btn['url'])] for btn in buttons
    ]
    markup = InlineKeyboardMarkup(keyboard)

    users = load_users()
    for user_id in users:
        try:
            bot.send_message(chat_id=user_id, text=text, reply_markup=markup)
            print(f"📤 Sent to {user_id}")
        except Exception as e:
            print(f"❌ Failed to send to {user_id}: {e}")


# Auto-fetch & send logic
def run_loop():
    while True:
        try:
            res = requests.get(FIREBASE_URL, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data and data.get("enabled"):
                    version = int(data.get("version", 0))
                    if version > get_last_version():
                        print("🔔 New message version detected! Sending...")
                        broadcast(data)
                        save_version(version)
                else:
                    print("⚠️ Message is disabled or empty.")
            else:
                print("❌ Firebase fetch failed with status:", res.status_code)
        except Exception as e:
            print("🔥 Error in loop:", e)
        time.sleep(10)


# Start bot and thread
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    updater.start_polling()
    threading.Thread(target=run_loop, daemon=True).start()
    updater.idle()  # Keep main thread alive