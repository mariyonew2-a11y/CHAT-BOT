import telebot
import os
import time
import re
import io
import requests
from flask import Flask
from threading import Thread

# --- [ CONFIGURATION ] ---
HAPUPPY_KEY = "sk-hapuppy-yiRDDBQsvG95vbX4MQJqjHdewyM0klOl2TDCujqED82J1VZR"
BASE_URL = "https://api.hapuppy.com/v1/chat/completions"
BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ STABILITY HELPERS ] ---
def safe_edit(chat_id, message_id, text):
    try:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown")
    except:
        bot.edit_message_text(text, chat_id, message_id, parse_mode=None)

def safe_send(chat_id, text, bio=None, filename=None):
    try:
        if bio:
            caption_box = (
                f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃    📂 **PARDHAN FILE** ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━┛\n"
                f"File: `{filename}`\n"
                f"Developer: @beast_harry"
            )
            return bot.send_document(chat_id, bio, caption=caption_box, parse_mode="Markdown")
        return bot.send_message(chat_id, text, parse_mode="Markdown")
    except:
        return bot.send_message(chat_id, text, parse_mode=None)

# --- [ AI ENGINE - ZERO MEMORY MODE ] ---
def get_hapuppy_response(user_input):
    headers = {
        "Authorization": f"Bearer {HAPUPPY_KEY}",
        "Content-Type": "application/json"
    }
    
    # Harry bhai, tokens bachane ke liye sirf current message bhej rahe hain
    payload = {
        "model": "gpt-4o-mini", # Agar ye error de toh dashboard se model name check karein
        "messages": [
            {"role": "system", "content": "You are BABA GPT by @beast_harry. Concise and smart. Code must be in triple backticks."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.6
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        res_data = response.json()
        
        if response.status_code == 200:
            return res_data['choices'][0]['message']['content']
        else:
            # Detailed Error from Hapuppy
            err_details = res_data.get('error', {}).get('message', 'Unknown Error')
            return f"❌ Hapuppy Error: {err_details}"
            
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# --- [ CODE TO FILE LOGIC ] ---
def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?[\s\n]*([\s\S]*?)```', text)
    
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            safe_send(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            # Extension detect logic
            lang = lang.strip().lower() if lang else ""
            if "html" in lang or "<html" in code[:100].lower(): ext = "html"
            elif "py" in lang or "import" in code[:100].lower(): ext = "py"
            elif "css" in lang: ext = "css"
            else: ext = lang if lang else "txt"
            
            filename = f"Pardhan_Source_{i+1}.{ext}"
            bio = io.BytesIO(code.encode('utf-8'))
            bio.name = filename
            safe_send(chat_id, "", bio=bio, filename=filename)
        return True
    return False

# --- [ COMMAND HANDLERS ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v5.7** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Welcome, **{name}**! I am BABA GPT, engineered for elite automation.\n\n"
        f"🚀 **Core Features:**\n"
        f"• **Hapuppy Engine:** High-level AI reasoning.\n"
        f"• **Code Extraction:** Instant files via triple backticks.\n"
        f"• **Token Saver:** Memory-free mode for max performance.\n\n"
        f"┃ Developer: @beast_harry ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    safe_send(message.chat.id, design)

@bot.message_handler(commands=['clear'])
def clear(message):
    # Memory already zero, but keeping for user satisfaction
    safe_send(message.chat.id, "🗑️ **System Reset.** Tokens optimized.")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # 🔍 Lens Emoji Search
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching...**", parse_mode="Markdown")
    
    response = get_hapuppy_response(message.text)
    
    if response.startswith("❌"):
        safe_edit(message.chat.id, status_msg.message_id, response)
        return

    # Check for files or text
    if not extract_and_send_code(message.chat.id, response):
        safe_edit(message.chat.id, status_msg.message_id, response)
    else:
        bot.delete_message(message.chat.id, status_msg.message_id)

# --- [ SERVER ] ---
@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    print("✅ BABA GPT v5.7 is Waking Up...")
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
