import telebot
import os
import requests
import io
import re
from flask import Flask
from threading import Thread
from duckduckgo_search import DDGS # Real-time search ke liye

# --- [ CONFIGURATION ] ---
SAMBA_KEY = "YAHAN_APNI_SAMBANOVA_KEY_DALO"
BASE_URL = "https://api.sambanova.ai/v1/chat/completions"
SELECTED_MODEL = "Meta-Llama-3.3-70B-Instruct"

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ WEB SEARCH LOGIC ] ---
def fetch_realtime_data(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except:
        return "No real-time data found."

# --- [ AI ENGINE - SEARCH ENABLED ] ---
def get_samba_response(user_input):
    # 1. Pehle internet par search karte hain
    web_data = fetch_realtime_data(user_input)
    
    headers = {
        "Authorization": f"Bearer {SAMBA_KEY}",
        "Content-Type": "application/json"
    }
    
    # 2. AI ko Internet ka "Context" dete hain
    payload = {
        "model": SELECTED_MODEL, 
        "messages": [
            {
                "role": "system", 
                "content": f"You are BABA GPT by @beast_harry. Use the following REAL-TIME INTERNET DATA to answer if needed: {web_data}"
            },
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

# --- [ STEP 3: CODE TO FILE LOGIC - AS IT IS ] ---
def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', text)
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
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
            bot.send_document(chat_id, bio, caption=f"📄 **Project File:** `{filename}`\n⚡ *Created by @beast\_harry*")
        return True
    return False

# --- [ HANDLERS - EXACTLY SAME ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        ⚡ **BABA GPT v6.5** ⚡        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Greetings, **{name}**! I am BABA GPT, now with **Real-Time Internet Access**.\n\n"
        f"I have been engineered by **@beast\_harry** to provide you with elite intelligence.\n\n"
        f"🚀 **Core Intelligence:**\n"
        f"• **Live Search:** Access to 2026 current affairs.\n"
        f"• **Instant Code:** Flawless scripts into files.\n"
        f"• **SambaNova Power:** Zero downtime performance.\n\n"
        f"┃ *Developed with passion by @beast\_harry* ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.reply_to(message, design, parse_mode="Markdown")
    except:
        bot.reply_to(message, design)

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching the Web...**", parse_mode="Markdown")
    
    response = get_samba_response(message.text)
    
    if response is None:
        bot.edit_message_text("❌ **Something went wrong.**", message.chat.id, status_msg.message_id)
        return

    if not extract_and_send_code(message.chat.id, response):
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        bot.delete_message(message.chat.id, status_msg.message_id)

@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
