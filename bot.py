import telebot
import os
import time
import re
import io
import requests
from flask import Flask
from threading import Thread

# --- [ HAPUPPY CONFIG ] ---
# Harry bhai, tumhari key yahan set kar di hai
HAPUPPY_KEY = "sk-hapuppy-yiRDDBQsvG95vbX4MQJqjHdewyM0klOl2TDCujqED82J1VZR"
BASE_URL = "https://api.hapuppy.com/v1/chat/completions"

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ AI ENGINE - ZERO MEMORY ] ---
def get_hapuppy_response(user_input):
    headers = {
        "Authorization": f"Bearer {HAPUPPY_KEY}",
        "Content-Type": "application/json"
    }
    
    # Zero Memory Logic: Sirf current message bhej rahe hain
    payload = {
        "model": "gpt-4o-mini", # Ye model fast hai aur credits bachata hai
        "messages": [
            {"role": "system", "content": "You are BABA GPT by @beast_harry. Always wrap code in triple backticks."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.6
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"API Error: {str(e)}")
        return f"❌ AI Error: Check Hapuppy Dashboard or Credits."

# --- [ STEP 3: CODE TO FILE LOGIC ] ---
def extract_and_send_code(chat_id, text):
    # Flexible regex to catch blocks
    code_blocks = re.findall(r'```(\w+)?[\s\n]*([\s\S]*?)```', text)
    
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            try:
                bot.send_message(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}", parse_mode="Markdown")
            except:
                bot.send_message(chat_id, f"🤖 BABA GPT Response:\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            ext = lang.strip().lower() if lang else "txt"
            if "html" in ext: ext = "html"
            elif "py" in ext: ext = "py"
            elif "c" == ext: ext = "c"
            
            filename = f"Pardhan_Source_{i+1}.{ext}"
            
            # --- [ SUNDAR CAPTION DESIGN ] ---
            caption_box = (
                f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃    📂 **PARDHAN FILE** ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━┛\n"
                f"File: `{filename}`\n"
                f"Developer: @beast_harry"
            )
            
            bio = io.BytesIO(code.encode('utf-8'))
            bio.name = filename
            try:
                bot.send_document(chat_id, bio, caption=caption_box, parse_mode="Markdown")
            except:
                bot.send_document(chat_id, bio, caption=caption_box)
        return True
    return False

# --- [ STEP 1: START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v5.7** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Welcome, **{name}**! I am BABA GPT, powered by the Beast Engine.\n\n"
        f"🚀 **Capabilities:**\n"
        f"• **Instant Logic:** Optimized for zero-latency response.\n"
        f"• **File Delivery:** Automated source code extraction.\n"
        f"• **Token Saver:** Memory-free mode for unlimited chat.\n\n"
        f"┃ Developer: @beast_harry ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.reply_to(message, design, parse_mode="Markdown")
    except:
        bot.reply_to(message, design)

# --- [ STEP 2: CHAT HANDLER ] ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # 🔍 Lens emoji searching status
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching...**", parse_mode="Markdown")
    
    response = get_hapuppy_response(message.text)
    
    if response.startswith("❌ AI Error:"):
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        return

    # Check for Code and send files
    if not extract_and_send_code(message.chat.id, response):
        # Normal Text Response (No Footer)
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        # Code bhej diya gaya hai, toh status delete kar do
        bot.delete_message(message.chat.id, status_msg.message_id)

# --- [ SERVER LOGIC ] ---
@app.route('/')
def home(): return "BABA_GPT_ONLINE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    print("✅ BABA GPT is waking up with Hapuppy...")
    Thread(target=run).start()
    bot.infinity_polling()
