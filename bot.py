# bot.py

import time
import requests
import json
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
FIREBASE_URL = 'https://free-7d474-default-rtdb.asia-southeast1.firebasedatabase.app/message.json'

bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher

USERS_FILE = 'users.json'
LAST_VERSION_FILE = 'last_version.txt'

# Load users
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Save users
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Start command handler
def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)
    update.message.reply_text("✅ Bot activated! You'll receive updates automatically.")

dispatcher.add_handler(CommandHandler('start', start))

# Load last version
def get_last_version():
    try:
        with open(LAST_VERSION_FILE, 'r') as f:
            return int(f.read())
    except:
        return -1

# Save new version
def save_version(version):
    with open(LAST_VERSION_FILE, 'w') as f:
        f.write(str(version))

# Send message to all users
def broadcast(message_data):
    text = message_data.get('text', '')
    buttons = message_data.get('buttons', [])

    keyboard = [
        [InlineKeyboardButton(btn['text'], url=btn['url'])] for btn in buttons
    ]
    markup = InlineKeyboardMarkup(keyboard)

    users = load_users()
    for user_id in users:
        try:
            bot.send_message(chat_id=user_id, text=text, reply_markup=markup)
        except Exception as e:
            print(f"Error sending to {user_id}: {e}")

# Background loop
def run():
    while True:
        try:
            res = requests.get(FIREBASE_URL)
            if res.status_code == 200:
                data = res.json()
                if data.get("enabled"):
                    version = int(data.get("version", 0))
                    if version > get_last_version():
                        print("🔔 New message detected! Broadcasting...")
                        broadcast(data)
                        save_version(version)
            else:
                print("Failed to fetch Firebase data")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(10)

# Start the bot
updater.start_polling()
print("🤖 Bot is running...")
run()