import telebot
import json
import requests
import os
import time
from groq import Groq
from flask import Flask
from threading import Thread

# --- [ MULTI-KEY CONFIG ] ---
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

def get_groq_client():
    global current_key_index
    return Groq(api_key=KEY_POOL[current_key_index])

def get_groq_response(user_id, user_input):
    global current_key_index
    
    if user_id not in chat_memories:
        chat_memories[user_id] = [{"role": "system", "content": "You are Pardhan AI by @beast_harry."}]
    
    chat_memories[user_id].append({"role": "user", "content": user_input})
    
    # Retry logic for 429 (Rate Limit)
    for _ in range(len(KEY_POOL)):
        try:
            client = get_groq_client()
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
                print(f"⚠️ Key {current_key_index} Limit Hit! Switching...")
                current_key_index = (current_key_index + 1) % len(KEY_POOL)
                continue
            else:
                return f"❌ Error: {str(e)}"
    
    return "❌ All Keys are currently exhausted. Please wait."

@bot.message_handler(commands=['start'])
def welcome(message):
    design = (
        f"⚡ **PARDHAN AI v5.0** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: **Multi-Key Engine Active**\n"
        f"Owner: **@beast\_harry**\n\n"
        f"Main ab pehle se zyada powerful hoon. "
        f"Unlimited talk mode on hai!\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

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
    except:
        bot.edit_message_text(final_design, message.chat.id, status_msg.message_id)

@app.route('/')
def home(): return "SYSTEM_STABLE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
