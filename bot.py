import telebot
import os
import time
from groq import Groq
from flask import Flask
from threading import Thread
from datetime import datetime

# --- [ CONFIG ] ---
GROQ_API_KEY = "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"
BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask('')

chat_memories = {}

def get_groq_response(user_id, user_input):
    if user_id not in chat_memories:
        # Initial System Prompt: Harry bhai ki identity set kar di
        chat_memories[user_id] = [{"role": "system", "content": "You are Pardhan AI, a pro-level assistant created by @beast_harry. Answer in a cool, professional, and helpful way."}]
    
    chat_memories[user_id].append({"role": "user", "content": user_input})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_memories[user_id],
            temperature=0.6,
            max_tokens=2048
        )
        
        ans = completion.choices[0].message.content
        chat_memories[user_id].append({"role": "assistant", "content": ans})
        
        # Memory limit taaki context clean rahe
        if len(chat_memories[user_id]) > 12:
            chat_memories[user_id] = [chat_memories[user_id][0]] + chat_memories[user_id][-10:]
            
        return ans
    except Exception as e:
        return f"❌ Groq API Error: {str(e)}"

# --- [ UI HANDLERS ] ---

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    welcome_design = (
        f"⚡ **PARDHAN AI v4.0** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Boliye **{name}** bhai, kaise aana hua?\n\n"
        f"Main Harry bhai ka signature AI project hoon. "
        f"Mere paas logic, coding aur har sawaal ka jawab hai.\n\n"
        f"🛠 **Designed & Developed by:**\n"
        f"👑 **@beast\_harry** (The Beast Master)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Use /clear to reset memory."
    )
    bot.reply_to(message, welcome_design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_memories.pop(message.from_user.id, None)
    bot.reply_to(message, "🗑️ **Memory Cleaned.**\nNaya session active hai.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # 1. "Thinking..." status send karo
    status_msg = bot.reply_to(message, "⚡ **Thinking...**", parse_mode="Markdown")
    
    # 2. Response fetch karo
    response = get_groq_response(message.from_user.id, message.text)
    
    final_design = (
        f"🤖 **PARDHAN INTELLIGENCE**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{response}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *By @beast\_harry*"
    )
    
    # 3. Message edit karo (with Crash Protection)
    try:
        # Pehle Markdown ke saath try karega
        bot.edit_message_text(final_design, message.chat.id, status_msg.message_id, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException:
        # Agar Markdown fail hua, toh bina formatting ke bhej dega (Taaki reply miss na ho)
        bot.edit_message_text(final_design, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error updating message: {str(e)}")

# --- [ SERVER ] ---
@app.route('/')
def home(): return "PARDHAN_AI_ACTIVE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    print("✅ Pardhan AI is waking up...")
    Thread(target=run).start()
    bot.infinity_polling()
