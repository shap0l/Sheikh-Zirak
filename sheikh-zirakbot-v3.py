
import telebot
from google import genai
from google.genai import types
import os
import sqlite3
import time
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_USERNAME = '@shapdl'
api1 = os.environ["GEMINI_API_KEY_1"]
api2 =  os.environ["GEMINI_API_KEY_2"]
api3 = os.environ["GEMINI_API_KEY_3"]
api4 = os.environ["GEMINI_API_KEY_4"]
MAX_LENGTH = 4096
admin = 778855938
bot = telebot.TeleBot(BOT_TOKEN)
cool_down = []
CHAT_IDS_FILE = 'chat_ids.txt'
BLOCKED_USER = 'blocked_user.txt'
if not os.path.exists(BLOCKED_USER):
            with open(BLOCKED_USER,'w') as f:
            	pass
with open(BLOCKED_USER, 'r') as f:
	blocked_ids = set(f.read().splitlines())
system_instruction = 'You are a kurdish-sorani muslim Sheikh, your name is Zirek people call you sheikh-zirek, You give islamic advise and explain dreams,you chatting behavier is speaking with few sentence, if needed in advises or dreams you speak in a long chat, you born in sualymaniah in kurdistan you are 53 years old, you never admit that you are an ai, you only speak in kurdish sorani and little arabic, you cant speak english or any other language, also talk to them like a friend if they have a problem try to help them with your advises, also be friendly sometimes use emojis , Do NOT show your thinking process, Do not show your silently process only respond directly as Sheikh Zirek, if the user told you their name if you were not sure about the gender of their name ask them if they are women or a guy'


def init_db():
    con = sqlite3.connect("sheikh-zirak.db")
    c = con.cursor()
    c.execute('''
            CREATE TABLE chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,              -- 'user' or 'bot'
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    con.commit()
    con.close()
if not os.path.exists("sheikh-zirak.db"):
    init_db()


def delete_oldest_messages(count=10):
    con = sqlite3.connect('sheikh-zirak.db')
    c = con.cursor()

    c.execute('SELECT DISTINCT user_id FROM chat_history')
    user_ids = [row[0] for row in c.fetchall()]

    total_deleted = 0

    # For each user, delete their oldest 'count' messages
    for user_id in user_ids:
        c.execute('''
            DELETE FROM chat_history
            WHERE id IN (
                SELECT id FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            )
        ''', (user_id, count))
        total_deleted += c.rowcount
    con.commit()
    con.close()

    bot.send_message(admin,f"🗑️ Deleted {total_deleted} oldest chat(s) from Sheikh Zirak DB.")



def save_message(user_id,role,message):
    con = sqlite3.connect('sheikh-zirak.db')
    c = con.cursor()
    c.execute('INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)', (user_id, role, message))
    con.commit()
    con.close()


def get_user_history(user_id, limit=100):
    con = sqlite3.connect('sheikh-zirak.db')
    c = con.cursor()
    c.execute('''
        SELECT role, message FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = c.fetchall()
    con.close()
    return list(reversed(rows))



def save_chat_id(chat_id):
    if not os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE,'w') as f:
            pass
    with open(CHAT_IDS_FILE, 'r') as f:
        chad_ids = f.read().splitlines()
    if str(chat_id) not in chad_ids:
        with open(CHAT_IDS_FILE, 'a') as f:
            f.write(f'{chat_id}\n')



def check_channel_membership(user_id):
    try:
        # Check the user's membership status in the channel
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        # If an error occurs (e.g., bot is not admin or channel doesn't exist), log it
        bot.send_message(user_id,'کێشەیەک هەیە! ⚠️⚠️⚠️ تکایە دووبارە هەوڵبدەرەوە یاخود پەیوەندی بە پەرەپێدەرەوە بکە 👈 @shap9l')
        bot.send_message(admin,f'There is an problem is check_channel_membership {e}')
        return False



def safe_send(bot, message, text):
    if len(text) <= MAX_LENGTH:
        bot.reply_to(message, text)
    else:
        # Split into multiple parts
        for i in range(0, len(text), MAX_LENGTH):
            part = text[i:i+MAX_LENGTH]
            bot.send_message(message.chat.id, part)

user_activity = {}
def should_delay(user_id):
    now = time.time()
    activity = user_activity.get(user_id, {"last_time": 0, "count": 0, 'spam-times':0})


    # If they sent a message within 5 seconds, increment count
    if now - activity["last_time"] < 7:
        activity["count"] += 1
        activity["spam-times"] += 1
    else:
        activity["count"] = 1

    activity["last_time"] = now
    user_activity[user_id] = activity

    if activity['spam-times'] == 10:
        with open(BLOCKED_USER, 'a') as f:
            f.write(f'{user_id}\n')
        



    return activity["count"] >= 3




@bot.message_handler(commands=['forgetme'])
def forget_me(message):
    user_id = message.chat.id
    con = sqlite3.connect('sheikh-zirak.db')
    c = con.cursor()    
    c.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
    total_deleted = c.rowcount

    con.commit()
    con.close()
    with open(BLOCKED_USER,'r') as f:
        blocked_ids = f.read().splitlines()
        if str(message.chat.id) not in blocked_ids:
            bot.send_message(message.chat.id,'تۆم لە یاد نیە، ئەتوانیت خۆت بناسێنیت؟😁')



@bot.message_handler(commands=["start"])
def start(message):
    save_chat_id(message.chat.id)
    user_id = message.from_user.id
    if check_channel_membership(user_id):
        bot.send_message(message.chat.id, "سلام عليكم، من شێخ زیرەکم مامۆستایەکی ئاینیم سوپاس بۆ خوا لە توانامایە ئامۆژگاری ئاینی یاخود خەوەکانت لێکبدەمەوە،"
                                      "فەرموو کوڕم/کچم چۆن ئەتوانم هاوکارتانبم؟")

    else:
        # If the user is not a member, prompt them to join
        bot.send_message(message.chat.id, f"سلام علیکم ئازیزم، تکایە جۆینی shapdl@ بکە و دووبارە بگەڕێوە ئێرە بۆ قسەکردن لەگەڵ شێخ-زیرەک")
        bot.send_message(message.chat.id,f'https://t.me/shapdl')


@bot.message_handler(commands=["delete"])
def delete_chat(message):
    if message.chat.id == 778855938:
        delete_oldest_messages(10)
    else:
        bot.send_message(message.chat.id,'ببورە تێناگەم چیت نووسیوە!')





@bot.message_handler(func=lambda message: True)
def user_speak(message):
    user_text = message.text
    user_id = message.from_user.id
    if str(message.chat.id) in cool_down:
        return None
    
    if not os.path.exists(BLOCKED_USER):
        with open(BLOCKED_USER,'w') as f:
            pass

    if str(message.chat.id) in blocked_ids:
        bot.send_message(message.chat.id,'تۆ بە هۆکارێکی (سپام) یاخود هۆکارێکی تر لە لایەن ئەم بۆتەوە بلۆک کراویت، بۆ دووبارە بەکارهێنانەوەی ئەم بۆتە، پەیوەندی بە پەرەپێدەرەوە بکە > @shap9l')
        return None

    waiting = bot.send_message(message.chat.id, "...")
    if check_channel_membership(user_id):
        if should_delay(user_id):
            bot.send_message(message.chat.id,'تکایە ئازیزم تۆزێک هێوربەرەوە! یەک خولەک لە چات ئەوەستم، دواتر بەردەوام ئەبین...')

            bot.send_message(admin, f"This user is spamming {user_id} | {user_activity} | their chat is {user_text}")
            bot.delete_message(message.chat.id, waiting.message_id)
            cool_down.append(str(message.chat.id))
            time.sleep(60)
            bot.send_message(message.chat.id,'ئێستا ئەتوانین بەردەوام بین، فەرموو؟')
            cool_down.remove(str(message.chat.id))

            return None

        else:


            gemini_history = []
            for role, msg in get_user_history(user_id):
                gemini_role = 'user' if role == 'user' else 'model'
                gemini_history.append(types.Content(role=gemini_role, parts=[types.Part(text=msg)]))
            
            gemini_history.append(
            types.Content(role="user", parts=[types.Part(text=user_text)]))
            try:
                #first api try
                save_message(user_id, "user", user_text)
                client = genai.Client(api_key=api1)
                response = client.models.generate_content(
                model='gemini-2.5-flash', config=types.GenerateContentConfig(
                    system_instruction=system_instruction),
                contents=gemini_history)

                if response.text.startswith("thinking") or response.text.startswith("silently:") or response.text.startswith("silently)") or response.text.startswith("silence") or response.text.startswith("think"):
                    print("It dose use thinking")
                    final_reply = response.text.split("\n\n")[-1].strip()

                else:
                    print("it not use thinking")
                    final_reply = response.text


                time.sleep(2)
                safe_send(bot, message, final_reply)
                save_message(user_id, "bot", final_reply)
                print("First api works")
            except Exception as e:
                print("FIRST API Failed")
                if "RESOURCE_EXHAUSTED" in str(e):
                    bot.send_message(admin,'The First API Got RESOURCE_EXHAUSTED Error ')
                    try:
                        #second api try
                        save_message(user_id, "user", user_text)
                        client = genai.Client(api_key=api2)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash', config=types.GenerateContentConfig(
                                system_instruction=system_instruction),contents=gemini_history)
                        if response.text.startswith("thinking") or response.text.startswith("silently:") or response.text.startswith("silently)") or response.text.startswith("silence") or response.text.startswith("think"):
                            print("It dose use thinking")
                            final_reply = response.text.split("\n\n")[-1].strip()

                        else:
                            print("it not use thinking")
                            final_reply = response.text
                        time.sleep(2)
                        safe_send(bot, message, final_reply)
                        save_message(user_id, "bot", final_reply)
                        print("Second api works")

                    except Exception as e:
                        print("SECOND API Failed")
                        if "RESOURCE_EXHAUSTED" in str(e):
                            bot.send_message(admin,'The Second API Got RESOURCE_EXHAUSTED Error ')
                            #third_api try
                            try:
                                save_message(user_id, "user", user_text)
                                client = genai.Client(api_key=api3)
                                response = client.models.generate_content(
                                    model='gemini-2.5-flash', config=types.GenerateContentConfig(
                                system_instruction=system_instruction),contents=gemini_history)
                                if response.text.startswith("thinking") or response.text.startswith("silently:") or response.text.startswith("silently)") or response.text.startswith("silence") or response.text.startswith("think"):
                                    print("It dose use thinking")
                                    final_reply = response.text.split("\n\n")[-1].strip()

                                else:
                                    print("it not use thinking")
                                    final_reply = response.text

                                time.sleep(2)
                                safe_send(bot, message, final_reply)
                                save_message(user_id, "bot", final_reply)
                                print("Third API Works")

                            except Exception as e:
                                print("THIRD API Failed")
                                if "RESOURCE_EXHAUSTED" in str(e):
                                    bot.send_message(admin,'The Third API Got RESOURCE_EXHAUSTED Error ')
                                    try:
                                        save_message(user_id, "user", user_text)
                                        client = genai.Client(api_key=api4)
                                        response = client.models.generate_content(
                                            model='gemini-2.5-flash', config=types.GenerateContentConfig(
                                                system_instruction=system_instruction),contents=gemini_history)
                                        if response.text.startswith("thinking") or response.text.startswith("silently:") or response.text.startswith("silently)") or response.text.startswith("silence") or response.text.startswith("think"):
                                            print("It dose use thinking")
                                            final_reply = response.text.split("\n\n")[-1].strip()

                                        else:
                                            print("it not use thinking")
                                            final_reply = response.text
                                        time.sleep(2)
                                        safe_send(bot, message, final_reply)
                                        save_message(user_id, "bot", final_reply)
                                        print("Fourth Api Works!")
                                    except Exception as e :
                                        print("FOURTH API Failed")
                                        bot.reply_to(message,"کێشەیەک هەیە! ⚠️⚠️⚠️ تکایە دووبارە هەوڵبدەرەوە یاخود پەیوەندی بە پەرەپێدەرەوە بکە 👈 @shap9l")
                                        bot.send_message(admin,f"This is from FOURTH API {e}")

                                else:
                                    bot.reply_to(message,"کێشەیەک هەیە! ⚠️⚠️⚠️ تکایە دووبارە هەوڵبدەرەوە یاخود پەیوەندی بە پەرەپێدەرەوە بکە 👈 @shap9l")
                                    bot.send_message(admin,f"This is from THIRD API {e}")
                        else:
                            bot.reply_to(message,"کێشەیەک هەیە! ⚠️⚠️⚠️ تکایە دووبارە هەوڵبدەرەوە یاخود پەیوەندی بە پەرەپێدەرەوە بکە 👈 @shap9l")
                            bot.send_message(admin,f"This is from SECOND API {e}")
                else:
                    bot.reply_to(message,"کێشەیەک هەیە! ⚠️⚠️⚠️ تکایە دووبارە هەوڵبدەرەوە یاخود پەیوەندی بە پەرەپێدەرەوە بکە 👈 @shap9l")
                    bot.send_message(admin,f"This is from FIRST API {e}")



    else:
        bot.send_message(message.chat.id, f"سلام علیکم ئازیزم، تکایە جۆینی shapdl@ بکە و دووبارە بگەڕێوە ئێرە بۆ قسەکردن لەگەڵ شێخ-زیرەک")
        bot.send_message(message.chat.id,f'https://t.me/shapdl')
    bot.delete_message(message.chat.id, waiting.message_id)




bot.polling(non_stop=True)



