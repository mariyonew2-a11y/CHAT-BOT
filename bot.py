import telebot
import os
import time
import json
import requests
from groq import Groq
from flask import Flask
from threading import Thread
from datetime import datetime

KEY_POOL = [
    "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",
    "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",
    "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",
    "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"
]
current_key_index = 0

BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

chat_memories = {}

def get_groq_response(user_id, user_input):
    global current_key_index
    
    if user_id not in chat_memories:
        chat_memories[user_id] = [{"role": "system", "content": "You are Pardhan AI, a pro-level assistant created by @beast_harry. Answer in a cool, professional, and helpful way."}]
    
    chat_memories[user_id].append({"role": "user", "content": user_input})
    
    for _ in range(len(KEY_POOL)):
        try:
            client = Groq(api_key=KEY_POOL[current_key_index])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_memories[user_id],
                temperature=0.6,
                max_tokens=2048
            )
            
            ans = completion.choices[0].message.content
            chat_memories[user_id].append({"role": "assistant", "content": ans})
            
            if len(chat_memories[user_id]) > 12:
                chat_memories[user_id] = [chat_memories[user_id][0]] + chat_memories[user_id][-10:]
                
            return ans

        except Exception as e:
            if "429" in str(e):
                current_key_index = (current_key_index + 1) % len(KEY_POOL)
                continue
            else:
                return f"❌ Groq API Error: {str(e)}"
    
    return "❌ All API keys exhausted for now. Please wait."

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
    
    status_msg = bot.reply_to(message, "⚡ **Thinking...**", parse_mode="Markdown")
    
    response = get_groq_response(message.from_user.id, message.text)
    
    final_design = (
        f"🤖 **PARDHAN INTELLIGENCE**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{response}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *By @beast\_harry*"
    )
    
    try:
        bot.edit_message_text(final_design, message.chat.id, status_msg.message_id, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException:
        bot.edit_message_text(final_design, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {str(e)}")

@app.route('/')
def home(): return "PARDHAN_AI_ACTIVE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    print("✅ Pardhan AI is waking up...")
    Thread(target=run).start()
    bot.infinity_polling()
