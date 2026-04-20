import telebot
import os
import time
import re
import io
import requests # SambaNova ke liye
from flask import Flask
from threading import Thread

# --- [ SINGLE API CONFIG ] ---
# Harry bhai, apni SambaNova key yahan dalo
SAMBA_KEY = "e15244fc-ca6f-449e-99a1-49e119ceccca"
BASE_URL = "https://api.sambanova.ai/v1/chat/completions"
SELECTED_MODEL = "Meta-Llama-3.3-70B-Instruct"

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ AI ENGINE - ZERO MEMORY ] ---
def get_groq_response(user_id, user_input):
    # Memory logic hata di gayi hai - Sirf current input jayega
    headers = {
        "Authorization": f"Bearer {SAMBA_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": SELECTED_MODEL, 
        "messages": [
            {"role": "system", "content": "You are BABA GPT, a world-class AI developed by @beast_harry. You provide top-tier logic and code."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.6,
        "max_tokens": 4000
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=40)
        res_data = response.json()
        if response.status_code == 200:
            return res_data['choices'][0]['message']['content']
        else:
            return None
    except Exception as e:
        return None

# --- [ STEP 3: CODE TO FILE LOGIC ] ---
def extract_and_send_code(chat_id, text):
    # Regex to find all code blocks
    code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', text)
    
    if code_blocks:
        # Code ke alawa jo text bacha hai wo bhej do
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            bot.send_message(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}", parse_mode="Markdown")
        
        for i, (lang, code) in enumerate(code_blocks):
            # File extension check
            ext = lang if lang else "txt"
            if "html" in ext.lower(): ext = "html"
            elif "python" in ext.lower() or "py" in ext.lower(): ext = "py"
            elif "c" == ext.lower(): ext = "c"
            
            filename = f"BABA_GPT_Project_{i+1}.{ext}"
            
            # File buffer creation (No physical file saved on Render)
            bio = io.BytesIO(code.encode('utf-8'))
            bio.name = filename
            # Note: underscore ko escape kiya hai taaki crash na ho (\_)
            bot.send_document(chat_id, bio, caption=f"📄 **Project File:** `{filename}`\n⚡ *Created by @beast\_harry*")
        return True
    return False

# --- [ STEP 1: START COMMAND DESIGN ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        ⚡ **BABA GPT v5.0** ⚡        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Greetings, **{name}**! I am BABA GPT, your high-performance AI companion.\n\n"
        f"I have been engineered by **@beast\_harry** to provide you with elite-level intelligence and flawless automation.\n\n"
        f"🚀 **Core Intelligence:**\n"
        f"• **Advanced Logic:** Capable of solving high-level problems.\n"
        f"• **Instant Code:** Delivers error-free scripts as downloadable files.\n"
        f"• **System Mastery:** Deep understanding of Python, C, and Web Arch.\n"
        f"• **Speed Optimized:** Powered by SambaNova for zero downtime.\n\n"
        f"┃ *Developed with passion by @beast\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear(message):
    bot.reply_to(message, "🗑️ **Memory Wiped.** Fresh session started.")

# --- [ STEP 2: PROCESSING & ERROR HANDLING ] ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Thinking with Buffer Animation
    status_msg = bot.reply_to(message, "🔄 **BABA GPT is Thinking...**", parse_mode="Markdown")
    
    response = get_groq_response(message.from_user.id, message.text)
    
    if response == "exhausted":
        bot.edit_message_text("⚠️ **System Error:** All circuits busy. Try again later.", message.chat.id, status_msg.message_id)
        return
    elif response is None:
        bot.edit_message_text("❌ **Something went wrong.** Please check your prompt.", message.chat.id, status_msg.message_id)
        return

    # Check and Send File if Code exists
    if not extract_and_send_code(message.chat.id, response):
        # Normal Text Response (if no code found)
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        # Code bhej diya gaya hai, thinking message hata do
        bot.delete_message(message.chat.id, status_msg.message_id)

# --- [ SERVER LOGIC ] ---
@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    print("✅ BABA GPT is waking up...")
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
