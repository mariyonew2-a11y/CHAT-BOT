import telebot
import os
import time
import re
import io
import requests
import google.generativeai as genai
from flask import Flask
from threading import Thread

# --- [ DUAL CONFIGURATION ] ---
# Harry bhai, dono keys yahan dalo. Agar koi ek nahi hai toh use khali "" chorr do.
GEMINI_KEY = "AIzaSyAfcad38XcDdF1ZDMVo07RPICg5sJkqfN0"
SAMBA_KEY = ""

# SambaNova Config
SAMBA_URL = "https://api.sambanova.ai/v1/chat/completions"
SAMBA_MODEL = "Meta-Llama-3.3-70B-Instruct"

# Gemini Config
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- [ HYBRID AI ENGINE ] ---
def get_ai_response(user_input):
    # System Instruction
    sys_msg = "You are BABA GPT by @beast_harry. Provide elite coding logic and files."

    # 1. PEHLE GEMINI TRY KARTE HAIN
    if GEMINI_KEY:
        try:
            prompt = f"System: {sys_msg}\nUser: {user_input}"
            response = gemini_model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Gemini Skip: {e}")

    # 2. AGAR GEMINI FAIL HUA TO SAMBANOVA TRY KARTE HAIN
    if SAMBA_KEY:
        try:
            headers = {"Authorization": f"Bearer {SAMBA_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": SAMBA_MODEL,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.6
            }
            res = requests.post(SAMBA_URL, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"SambaNova Skip: {e}")

    return None

# --- [ CODE TO FILE LOGIC - AS IT IS ] ---
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
            # Escape underscore for @beast_harry
            bot.send_document(chat_id, bio, caption=f"📄 **Project File:** `{filename}`\n⚡ *Created by @beast\_harry*")
        return True
    return False

# --- [ START COMMAND ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃        ⚡ **BABA GPT** ⚡        ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Greetings, **{name}**! I am BABA GPT Hybrid.\n\n"
        f"I am powered by **Dual Engines** (Gemini + SambaNova) for 100% uptime.\n\n"
        f"🚀 **Features:**\n"
        f"• **Hybrid Failover:** Always active logic.\n"
        f"• **Code Extraction:** Auto-file delivery.\n"
        f"• **Zero Memory:** Maximum token efficiency.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.reply_to(message, design, parse_mode="Markdown")
    except:
        bot.reply_to(message, design)

# --- [ CHAT HANDLER ] ---
@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Thinking...**", parse_mode="Markdown")
    
    response = get_ai_response(message.text)
    
    if response is None:
        bot.edit_message_text("❌ **Dono APIs fail ho gayi.** Keys check karo Harry bhai.", message.chat.id, status_msg.message_id)
        return

    if not extract_and_send_code(message.chat.id, response):
        try:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        except:
            bot.edit_message_text(response, message.chat.id, status_msg.message_id)
    else:
        bot.delete_message(message.chat.id, status_msg.message_id)

# --- [ SERVER LOGIC ] ---
@app.route('/')
def home(): return "BABA_GPT_HYBRID_ONLINE"

if __name__ == "__main__":
    print("✅ BABA GPT v7.0 Hybrid is Waking Up...")
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
