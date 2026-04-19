import telebot
import os
import requests
import io
import re
from flask import Flask
from threading import Thread

# --- [ SAMBANOVA CONFIG ] ---
SAMBA_KEY = "7bd1589a-96fc-4fe4-811b-e1e42ba2098c"
BASE_URL = "https://api.sambanova.ai/v1/chat/completions"

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ AI ENGINE - SAMBANOVA POWER ] ---
def get_samba_response(user_input):
    headers = {
        "Authorization": f"Bearer {SAMBA_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        # 'llama3-1-70b' fast hai, 'llama3-1-405b' sabse smart hai
        "model": "llama3-1-70b", 
        "messages": [
            {"role": "system", "content": "You are BABA GPT by @beast_harry. You are a world-class AI. Provide logic and code in triple backticks."},
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
            return f"❌ Samba Error: {res_data.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# --- [ CODE EXTRACTOR & FILE LOGIC ] ---
def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?[\s\n]*([\s\S]*?)```', text)
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            bot.send_message(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            lang = lang.strip().lower() if lang else ""
            if "html" in lang or "<html" in code[:100].lower(): ext = "html"
            elif "py" in lang or "import" in code[:100].lower(): ext = "py"
            else: ext = lang if lang else "txt"
            
            filename = f"Pardhan_Source_{i+1}.{ext}"
            caption_box = (
                f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃    📂 **PARDHAN FILE** ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━┛\n"
                f"File: `{filename}`\n"
                f"Developer: @beast_harry"
            )
            bio = io.BytesIO(code.encode('utf-8'))
            bio.name = filename
            bot.send_document(chat_id, bio, caption=caption_box)
        return True
    return False

# --- [ HANDLERS ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v5.8** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Greetings! I am BABA GPT, powered by SambaNova's Elite Engine.\n\n"
        f"🚀 **Specialities:**\n"
        f"• **Hacker Logic:** Advanced C and Python solutions.\n"
        f"• **Instant Files:** Code delivered as downloadable source.\n"
        f"• **High Limits:** Optimized for long-range performance.\n\n"
        f"┃ Developer: @beast_harry ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design)

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching...**")
    
    response = get_samba_response(message.text)
    
    if not extract_and_send_code(message.chat.id, response):
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode=None)
    else:
        bot.delete_message(message.chat.id, status_msg.message_id)

@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
