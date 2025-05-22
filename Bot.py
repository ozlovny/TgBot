import telebot
import sqlite3

TOKEN = 'token'
bot = telebot.TeleBot('token')

# Создаём или подключаемся к базе данных SQLite
conn = sqlite3.connect('referral_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Создаём таблицу пользователей (если не существует)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    UNIQUE(user_id)
)
''')
conn.commit()

def user_exists(user_id):
    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None

def add_user(user_id, referrer_id=None):
    try:
        cursor.execute('INSERT INTO users (user_id, referrer_id) VALUES (?, ?)', (user_id, referrer_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # пользователь уже есть

def count_referrals(user_id):
    cursor.execute('SELECT COUNT(*) FROM users WHERE referrer_id = ?', (user_id,))
    return cursor.fetchone()[0]

@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    args = message.text.split()

    referrer_id = None
    if len(args) > 1:
        try:
            candidate = int(args[1])
            if candidate != user_id and user_exists(candidate):
                referrer_id = candidate
        except ValueError:
            pass

    if not user_exists(user_id):
        add_user(user_id, referrer_id)

    bot.send_message(message.chat.id, "Привет! Добро пожаловать в реферального бота.\n"
                                      "Используйте /reflink, чтобы получить свою реферальную ссылку.\n"
                                      "Используйте /refcount, чтобы узнать, сколько вы пригласили.")

@bot.message_handler(commands=['reflink'])
def reflink_handler(message):
    user_id = message.from_user.id
    bot_username = bot.get_me().username
    link = f"https://t.me/{bot_username}?start={user_id}"
    bot.send_message(message.chat.id, f"Ваша реферальная ссылка:\n{link}")

@bot.message_handler(commands=['refcount'])
def refcount_handler(message):
    user_id = message.from_user.id
    count = count_referrals(user_id)
    bot.send_message(message.chat.id, f"Вы пригласили {count} человек(а).")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
