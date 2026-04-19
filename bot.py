import telebot
import os
import time
import re
import io
import requests
from flask import Flask
from threading import Thread

# --- [ SAMBANOVA CONFIG ] ---
# Harry bhai, apni SambaNova key yahan dalo
SAMBA_KEY = "7bd1589a-96fc-4fe4-811b-e1e42ba2098c"
BASE_URL = "https://api.sambanova.ai/v1/chat/completions"
# Screenshot waala exact model name
SELECTED_MODEL = "Meta-Llama-3.3-70B-Instruct"

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ AI ENGINE - ZERO MEMORY ] ---
def get_samba_response(user_input):
    headers = {
        "Authorization": f"Bearer {SAMBA_KEY}",
        "Content-Type": "application/json"
    }
    
    # Memory wala part poora hata diya hai - Fresh Request only
    payload = {
        "model": SELECTED_MODEL, 
        "messages": [
            {"role": "system", "content": "You are BABA GPT by @beast_harry. Provide logic and code in triple backticks."},
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
            return f"❌ Samba Error: {res_data.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# --- [ CODE TO FILE LOGIC ] ---
def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', text)
    
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            # Markdown error se bachne ke liye try-except dalo
            try:
                bot.send_message(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}", parse_mode="Markdown")
            except:
                bot.send_message(chat_id, f"🤖 BABA GPT Response:\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            ext = lang if lang else "txt"
            if "html" in ext.lower(): ext = "html"
            elif "python" in ext.lower() or "py" in ext.lower(): ext = "py"
            elif "c" == ext.lower(): ext = "c"
            
            filename = f"BABA_GPT_Project_{i+1}.{ext}"
            bio = io.BytesIO(code.encode('utf-8'))
            bio.name = filename
            
            # Caption mein underscore ko escape kiya hai taaki Error 400 na aaye
            caption_text = f"📄 **Project File:** `{filename}`\n⚡ *Created by @beast\_harry*"
            try:
                bot.send_document(chat_id, bio, caption=caption_text, parse_mode="Markdown")
            except:
                bot.send_document(chat_id, bio, caption=caption_text.replace("*", ""))
        return True
    return False

# --- [ START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v6.0** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Greetings, **{name}**! I am BABA GPT, your high-performance AI companion.\n\n"
        f"I have been engineered by **@beast\_harry** to provide you with elite-level intelligence and flawless automation.\n\n"
        f"🚀 **Core Intelligence:**\n"
        f"• **Advanced Logic:** Capable of solving high-level problems.\n"
        f"• **Instant Code:** Delivers error-free scripts as downloadable files.\n"
        f"• **System Mastery:** Deep understanding of Python, C, and Web Arch.\n"
        f"• **SambaNova Power:** Zero downtime with elite speed.\n\n"
        f"┃ *Developed with passion by @beast\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.reply_to(message, design, parse_mode="Markdown")
    except:
        bot.reply_to(message, design)

@bot.message_handler(commands=['clear'])
def clear(message):
    bot.reply_to(message, "🗑️ **Memory Wiped.** Tokens optimized.")

# --- [ CHAT HANDLER ] ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Lens Name Fix as requested: Thinking status
    status_msg = bot.reply_to(message, "🔄 **BABA GPT is Thinking...**", parse_mode="Markdown")
    
    response = get_samba_response(message.text)
    
    if response.startswith("❌"):
        bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        return

    # Check and Send File if Code exists
    if not extract_and_send_code(message.chat.id, response):
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        bot.delete_message(message.chat.id, status_msg.message_id)

# --- [ SERVER LOGIC ] ---
@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    print("✅ BABA GPT is waking up with SambaNova...")
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
