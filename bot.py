import telebot
import json
import requests
import os
import time
from datetime import datetime
from flask import Flask
from threading import Thread
from telebot import types

# --- [ CONFIG ] ---
# Token Render ke Env Variables mein 'BOT_TOKEN' naam se daalna
BOT_TOKEN = os.environ.get('8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

API_URL = "https://plai.chat/api/web/chat/send"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://plai.chat",
    "Referer": "https://plai.chat/",
}

# Local Memory (RAM based)
chat_history = {}

# --- [ AI ENGINE ] ---
def fetch_nemotron_response(user_id, prompt):
    if user_id not in chat_history:
        chat_history[user_id] = []
    
    payload = {
        "message": prompt,
        "history": chat_history[user_id],
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "attachments": [],
        "conversationStartedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "zdr": False
    }

    try:
        res = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60, stream=True)
        if not res.ok: return "❌ **System Busy:** AI Engine response nahi de raha."

        full_text = ""
        for line in res.iter_lines():
            if line:
                chunk = line.decode("utf-8")
                if chunk.startswith("data: "):
                    data = json.loads(chunk[6:])
                    if data.get("type") == "content":
                        full_text = data.get("text", "")
                    if data.get("done"): break
        
        # Memory Update (Role based)
        chat_history[user_id].append({"role": "user", "content": prompt})
        chat_history[user_id].append({"role": "assistant", "content": full_text})
        
        # Keep last 10 messages for context
        if len(chat_history[user_id]) > 10:
            chat_history[user_id] = chat_history[user_id][-10:]
            
        return full_text.strip()
    except Exception as e:
        return f"❌ **Error:** Connection lost. ({str(e)})"

# --- [ UI HANDLERS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"💀 **PARDHAN AI v1.0** 💀\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Welcome, **{name}**!\n\n"
        f"Main NVIDIA Nemotron-3 engine par chalta hoon. "
        f"Mujhse kuch bhi puchiye, main sab jaanta hoon.\n\n"
        f"🚀 **Commands:**\n"
        f"• /clear - Purani baatein bhulane ke liye\n"
        f"• /help - Madat ke liye\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Developer: @beast\_harry"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear_memory(message):
    chat_history.pop(message.from_user.id, None)
    bot.reply_to(message, "🗑️ **Memory Cleaned!**\nAb hum ek naye sire se baat kar sakte hain.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def chat_logic(message):
    # Typing action for professional feel
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Send temporary status message
    status_msg = bot.reply_to(message, "⚡ **Thinking...**", parse_mode="Markdown")
    
    response = fetch_nemotron_response(message.from_user.id, message.text)
    
    # Final Output Design
    final_output = (
        f"🤖 **Nemotron AI**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{response}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    bot.edit_message_text(final_output, message.chat.id, status_msg.message_id, parse_mode="Markdown")

# --- [ WEB SERVER FOR RENDER ] ---
@app.route('/')
def home(): return "SERVICE_ACTIVE"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("✅ Bot is Polling...")
    bot.infinity_polling()
