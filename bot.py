import telebot
import os
import time
import re
import io
from groq import Groq
from flask import Flask
from threading import Thread

# --- [ CONFIG ] ---
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

# --- [ SAFE SEND/EDIT HELPER ] ---
def safe_edit(chat_id, message_id, text, parse_mode="Markdown"):
    try:
        bot.edit_message_text(text, chat_id, message_id, parse_mode=parse_mode)
    except:
        try:
            bot.edit_message_text(text, chat_id, message_id, parse_mode=None)
        except: pass

def safe_send(chat_id, text, parse_mode="Markdown", caption=None, bio=None):
    try:
        if bio:
            return bot.send_document(chat_id, bio, caption=text, parse_mode=parse_mode)
        return bot.send_message(chat_id, text, parse_mode=parse_mode)
    except:
        if bio:
            return bot.send_document(chat_id, bio, caption=text, parse_mode=None)
        return bot.send_message(chat_id, text, parse_mode=None)

# --- [ AI ENGINE ] ---
def get_groq_response(user_id, user_input):
    global current_key_index
    if user_id not in chat_memories:
        chat_memories[user_id] = [{"role": "system", "content": "You are BABA GPT, a premium AI engineered by @beast_harry. Provide elite and high-quality responses."}]
    
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

# --- [ FILE HANDLER ] ---
def extract_and_send_code(chat_id, text):
    code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', text)
    
    if code_blocks:
        clean_text = re.sub(r'```[\s\S]*?```', '', text).strip()
        if clean_text:
            safe_send(chat_id, f"🤖 **BABA GPT Response:**\n\n{clean_text}")
        
        for i, (lang, code) in enumerate(code_blocks):
            ext = lang.strip() if lang else "txt"
            if "html" in ext.lower(): ext = "html"
            elif "py" in ext.lower(): ext = "py"
            elif "c" == ext.lower(): ext = "c"
            
            filename = f"Pardhan_Project_{i+1}.{ext}"
            caption_box = (
                f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃    📂 **PARDHAN FILE** ┃\n"
                f"┗━━━━━━━━━━━━━━━━━━━━┛\n"
                f"File: `{filename}`\n"
                f"Developer: @beast_harry"
            )
            
            bio = io.BytesIO(code.encode('utf-8'))
            bio.name = filename
            safe_send(chat_id, caption_box, bio=bio)
        return True
    return False

# --- [ HANDLERS ] ---
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    # Yahan underscore ko escape kiya gaya hai taaki crash na ho
    design = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃       ⚡ **BABA GPT v5.2** ⚡       ┃\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"Welcome, **{name}**! I am BABA GPT, an elite artificial intelligence designed for precision and power.\n\n"
        f"🚀 **Core Specialities:**\n"
        f"• **Strategic Logic:** Solving high-complexity challenges.\n"
        f"• **Instant Architecture:** Rapid generation of structured code.\n"
        f"• **Full-Stack Knowledge:** Mastery over modern tech stacks.\n"
        f"• **Adaptive Intelligence:** Evolving with every interaction.\n\n"
        f"┃ Developer: @beast\_harry ┃\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    safe_send(message.chat.id, design)

@bot.message_handler(commands=['clear'])
def clear(message):
    chat_memories.pop(message.from_user.id, None)
    safe_send(message.chat.id, "🗑️ **Memory Cleaned.** New session active.")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    # 🔍 Lens Emoji Search status
    status_msg = bot.reply_to(message, "🔍 **BABA GPT is Searching...**", parse_mode="Markdown")
    
    response = get_groq_response(message.from_user.id, message.text)
    
    if response == "exhausted":
        safe_edit(message.chat.id, status_msg.message_id, "❌ **Service Busy:** Try again in a minute.")
        return
    elif response is None:
        safe_edit(message.chat.id, status_msg.message_id, "❌ **Connection Error:** Something went wrong.")
        return

    # Check for Code & Files
    if not extract_and_send_code(message.chat.id, response):
        # Agar sirf text hai toh safely edit karo
        safe_edit(message.chat.id, status_msg.message_id, response)
    else:
        # Agar code bhej diya hai toh status delete kar do
        bot.delete_message(message.chat.id, status_msg.message_id)

@app.route('/')
def home(): return "BABA_GPT_ONLINE"

if __name__ == "__main__":
    print("✅ BABA GPT is waking up...")
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
