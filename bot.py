import telebot
import os
import requests
import io
import re
from flask import Flask
from threading import Thread

# --- [ CONFIGURATION ] ---
# Harry bhai, apni SambaNova key yahan dalo
SAMBA_KEY = "YAHAN_APNI_SAMBANOVA_KEY_DALO"
BASE_URL = "https://api.sambanova.ai/v1/chat/completions"
# Screenshot ke hisaab se sabse best model yahi hai
SELECTED_MODEL = "Meta-Llama-3.3-70B-Instruct"

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ AI ENGINE - ZERO MEMORY MODE ] ---
def get_samba_response(user_input):
    headers = {
        "Authorization": f"Bearer {SAMBA_KEY}",
        "Content-Type": "application/json"
    }
    
    # Harry bhai, yahan memory save nahi ho rahi, har baar fresh request jayegi
    payload = {
        "model": SELECTED_MODEL, 
        "messages": [
            {
                "role": "system", 
                "content": "You are BABA GPT, developed by @beast_harry. You are a world-class AI. Provide code ONLY if asked. If giving code, always use triple backticks."
            },
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=40)
        res_data = response.json()
        
        if response.status_code == 200:
            return res_data['choices'][0]['message']['content']
        else:
            err = res_data.get('error', {}).get('message', 'Unknown Error')
            return f"❌ Samba Error: {err}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# --- [ CODE TO FILE LOGIC - PARDHAN DESIGN ] ---
def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?[\s\n]*([\s\S]*?)```', text)
    
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            try:
                bot.send_message(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}", parse_mode="Markdown")
            except:
                bot.send_message(chat_id, f"🤖 BABA GPT Response:\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            lang = lang.strip().lower() if lang else ""
            if "html" in lang or "<html" in code[:100].lower(): ext = "html"
            elif "py" in lang or "import" in code[:100].lower(): ext = "py"
            else: ext = lang if lang else "txt"
            
            filename = f"Pardhan_Source_{i+1}.{ext}"
            
            # Harry bhai, ye raha tumhara "PARDHAN FILE" box design
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

# --- [ START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v6.0** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Welcome, **{name}**! I am BABA GPT, your high-performance AI companion.\n\n"
        f"I have been engineered by **@beast\_harry** to provide you with elite-level intelligence.\n\n"
        f"🚀 **Core Specialities:**\n"
        f"• **SambaNova Engine:** Next-gen reasoning speed.\n"
        f"• **Instant Files:** Code delivered as downloadable source.\n"
        f"• **Token Optimized:** Memory-free mode for max efficiency.\n\n"
        f"┃ Developer: @beast_harry ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

# --- [ CHAT HANDLER ] ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # FIXED: "Searching..." status as requested
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching...**", parse_mode="Markdown")
    
    response = get_samba_response(message.text)
    
    if response.startswith("❌"):
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        return

    # Check and Send File if Code exists
    if not extract_and_send_code(message.chat.id, response):
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        # File bhej di gayi, thinking message delete kar do
        bot.delete_message(message.chat.id, status_msg.message_id)

# --- [ SERVER LOGIC ] ---
@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    print("✅ BABA GPT v6.0 is Waking Up with SambaNova Power...")
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
