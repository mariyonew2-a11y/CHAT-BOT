import telebot
import json
import requests
import os
import time
from datetime import datetime, timezone
from flask import Flask
from threading import Thread
from telebot import types

# --- [ CONFIG ] ---
# Agar Render pe Env Variable set nahi kiya hai toh yahan token daal do
BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

API_URL = "https://plai.chat/api/web/chat/send"
chat_history = {}

# --- [ AI ENGINE ] ---
def fetch_nemotron_response(user_id, prompt):
    if user_id not in chat_history:
        chat_history[user_id] = []
    
    session = requests.Session()
    
    # ISO format fix for 2026 standards
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    payload = {
        "message": prompt,
        "history": chat_history[user_id],
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "attachments": [],
        "conversationStartedAt": current_time,
        "zdr": False
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/event-stream",
        "Referer": "https://plai.chat/",
        "Origin": "https://plai.chat",
        "Content-Type": "application/json"
    }

    try:
        res = session.post(API_URL, headers=headers, json=payload, timeout=60, stream=True)
        
        if res.status_code == 403:
            return "❌ **Security Block:** Render ka IP block hai. Termux mein try karein."
        if res.status_code != 200:
            return f"❌ **System Busy:** Error Code {res.status_code}"

        full_text = ""
        for line in res.iter_lines():
            if line:
                chunk = line.decode("utf-8")
                if chunk.startswith("data: "):
                    try:
                        data = json.loads(chunk[6:])
                        if data.get("type") == "content":
                            full_text = data.get("text", "")
                        if data.get("done"): break
                    except: continue
        
        if not full_text: return "⚠️ **AI Engine:** Khali response mila."

        # Memory Management
        chat_history[user_id].append({"role": "user", "content": prompt})
        chat_history[user_id].append({"role": "assistant", "content": full_text})
        
        if len(chat_history[user_id]) > 10:
            chat_history[user_id] = chat_history[user_id][-10:]
            
        return full_text.strip()
    except Exception as e:
        return f"❌ **Connection Error:** {str(e)}"

# --- [ UI HANDLERS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"💀 **PARDHAN AI v2.0** 💀\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Boliye **{name}** bhai, kya haal chaal?\n\n"
        f"NVIDIA Nemotron-3 engine active hai.\n\n"
        f"🚀 **Quick Commands:**\n"
        f"• /clear - Purani yaadein mitao\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Owner: @beast\\_harry"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear_memory(message):
    chat_history.pop(message.from_user.id, None)
    bot.reply_to(message, "🗑️ **Memory Cleaned!**", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def chat_logic(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "⚡ **Thinking...**", parse_mode="Markdown")
    
    response = fetch_nemotron_response(message.from_user.id, message.text)
    
    final_output = (
        f"🤖 **Nemotron AI**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{response}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    bot.edit_message_text(final_output, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# --- [ SERVER LOGIC ] ---
@app.route('/')
def home(): return "SYSTEM_ONLINE"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
