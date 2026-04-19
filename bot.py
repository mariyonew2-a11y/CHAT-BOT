import telebot
import os
from groq import Groq
from flask import Flask
from threading import Thread

# --- [ CONFIG ] ---
# Groq API Key: https://console.groq.com/keys
GROQ_API_KEY = "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"
BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask('')

chat_memories = {}

def get_groq_response(user_id, user_input):
    if user_id not in chat_memories:
        chat_memories[user_id] = []
    
    chat_memories[user_id].append({"role": "user", "content": user_input})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=chat_memories[user_id],
            temperature=0.7,
            max_tokens=1024,
            stream=False
        )
        
        ans = completion.choices[0].message.content
        chat_memories[user_id].append({"role": "assistant", "content": ans})
        
        if len(chat_memories[user_id]) > 10:
            chat_memories[user_id] = chat_memories[user_id][-10:]
            
        return ans
    except Exception as e:
        return f"❌ Error: {str(e)}"

@bot.message_handler(commands=['start'])
def welcome(message):
    design = (
        f"⚡ **PARDHAN GROQ AI** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: **Online & Fast**\n"
        f"Model: **Llama 3.1 (70B)**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Puchiye Harry bhai, kya madad karun?"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_memories.pop(message.from_user.id, None)
    bot.reply_to(message, "🗑️ Memory cleared!")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    response = get_groq_response(message.from_user.id, message.text)
    
    final_msg = (
        f"🤖 **Groq Assistant**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{response}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, final_msg, parse_mode="Markdown")

@app.route('/')
def home(): return "RUNNING"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
