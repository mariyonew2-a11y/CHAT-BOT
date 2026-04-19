import telebot
import os
import time
from groq import Groq
from flask import Flask
from threading import Thread
from datetime import datetime

GROQ_API_KEY = "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"
BOT_TOKEN = "8693996706:AAFhDMaiIPwps8woQvHSuQUpALSn5VsAR9Q"

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask('')

chat_memories = {}

def get_groq_response(user_id, user_input):
    if user_id not in chat_memories:
        chat_memories[user_id] = [{"role": "system", "content": "You are Pardhan AI, a powerful and logical assistant created by @beast_harry. You are smart, fast, and professional."}]
    
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
        
        if len(chat_memories[user_id]) > 12:
            chat_memories[user_id] = [chat_memories[user_id][0]] + chat_memories[user_id][-10:]
            
        return ans
    except Exception as e:
        return f"❌ System Error: {str(e)}"

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    welcome_design = (
        f"⚡ **PARDHAN AI v3.0** ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Greetings, **{name}**!\n\n"
        f"Main ek extreme-level AI assistant hoon, jise **@beast\_harry** ne design kiya hai. "
        f"Mere dimaag mein Llama-3.3 ki raftar aur Harry bhai ka logic hai.\n\n"
        f"🚀 **My Capabilities:**\n"
        f"• Instant Logical Reasoning\n"
        f"• Pro Coding & Debugging\n"
        f"• Advanced Creative Analysis\n"
        f"• 24/7 Beast Mode Active\n\n"
        f"Main aam bots ki tarah nahi hoon, main Harry bhai ka signature project hoon.\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"**OWNER:** @beast\_harry 👑"
    )
    bot.reply_to(message, welcome_design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_memories.pop(message.from_user.id, None)
    bot.reply_to(message, "🗑️ **Memory Wiped.**\nNaya session shuru kijiye.", parse_mode="Markdown")

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
        f"⚡ *Powered by @beast\_harry*"
    )
    
    try:
        bot.edit_message_text(final_design, message.chat.id, status_msg.message_id, parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, final_design, parse_mode="Markdown")

@app.route('/')
def home(): return "SERVICE_ONLINE"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    print("✅ Pardhan AI is waking up...")
    Thread(target=run).start()
    bot.infinity_polling()
