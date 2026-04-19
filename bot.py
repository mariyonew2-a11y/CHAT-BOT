import telebot
import os
import time
import re
import io
from groq import Groq
from flask import Flask
from threading import Thread

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
        chat_memories[user_id] = [{"role": "system", "content": "You are BABA GPT, a premium AI engineered by @beast_harry. You provide sharp, elite-level responses."}]
    
    chat_memories[user_id].append({"role": "user", "content": user_input})
    
    for _ in range(len(KEY_POOL)):
        try:
            client = Groq(api_key=KEY_POOL[current_key_index])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_memories[user_id],
                temperature=0.6,
                max_tokens=4000
            )
            ans = completion.choices[0].message.content
            chat_memories[user_id].append({"role": "assistant", "content": ans})
            return ans
        except Exception as e:
            if "429" in str(e):
                current_key_index = (current_key_index + 1) % len(KEY_POOL)
                continue
            else: return None
    return "exhausted"

def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', text)
    
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            bot.send_message(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            ext = lang if lang else "txt"
            if "html" in ext.lower(): ext = "html"
            elif "py" in ext.lower(): ext = "py"
            elif "c" == ext.lower(): ext = "c"
            
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
            bot.send_document(chat_id, bio, caption=caption_box, parse_mode="Markdown")
        return True
    return False

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v5.1** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Welcome, **{name}**! I am BABA GPT, an elite artificial intelligence designed for precision and power.\n\n"
        f"🚀 **Core Specialities:**\n"
        f"• **Strategic Logic:** Solving high-complexity challenges.\n"
        f"• **Instant Architecture:** Rapid generation of structured code.\n"
        f"• **Full-Stack Knowledge:** Mastery over modern tech stacks.\n"
        f"• **Adaptive Intelligence:** Evolving with every interaction.\n\n"
        f"┃ Developer: @beast_harry ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, design, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_memories.pop(message.from_user.id, None)
    bot.reply_to(message, "🗑️ **Memory Cleaned.** New session is active.")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching...**", parse_mode="Markdown")
    
    response = get_groq_response(message.from_user.id, message.text)
    
    if response == "exhausted":
        bot.edit_message_text("❌ **Service Busy:** Please retry in a moment.", message.chat.id, status_msg.message_id)
        return
    elif response is None:
        bot.edit_message_text("❌ **Something went wrong.** Try again.", message.chat.id, status_msg.message_id)
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
