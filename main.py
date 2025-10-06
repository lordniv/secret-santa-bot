import os
import logging
import random
from datetime import datetime
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    Filters,
    CallbackContext
)

# --- Конфигурация ---
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    exit(1)

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для создания комнаты
SETTING_NAME, SETTING_DESCRIPTION, SETTING_BUDGET, SETTING_DATE = range(4)
WISHES, = range(4, 5)

# Временное хранилище
rooms = {}
user_rooms = {}
pending_registrations = {}
user_wishes = {}

# --- Вспомогательные функции ---
def generate_room_code():
    import string
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

def shuffle_participants(participants):
    if len(participants) < 2:
        return []
    
    shuffled = participants[:]
    for attempt in range(100):
        random.shuffle(shuffled)
        valid = True
        for i in range(len(participants)):
            if participants[i] == shuffled[i]:
                valid = False
                break
        if valid:
            return list(zip(participants, shuffled))
    
    shuffled = participants[1:] + [participants[0]]
    return list(zip(participants, shuffled))

# --- Команды бота ---
def start(update: Update, context: CallbackContext):
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['📋 Мои игры', '✏️ Мои пожелания', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🎅 *Добро пожаловать в Тайного Санту!*\n\n"
        "Я помогу вам организовать обмен подарками. Вы можете:\n"
        "- Создать новую игру\n"
        "- Присоединиться к существующей игре\n"
        "- Указать свои пожелания к подаркам\n"
        "- Посмотреть свои активные игры\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext):
    help_text = """
*🎅 Как организовать Тайного Санту:*

1. *Создайте игру* - нажмите "🎅 Создать игру"
2. *Укажите пожелания* - нажмите "✏️ Мои пожелания"
3. *Пригласите друзей* - поделитесь кодом комнаты
4. *Дождитесь регистрации* - все участники должны присоединиться
5. *Проведите жеребьевку* - когда все готовы
6. *Обмен подарками!* - каждый узнает, кому дарить и его пожелания

*Команды:*
/start - главное меню
/help - эта справка
/cancel - отменить текущее действие

*Приятной игры!* 🎄
    """
    update.message.reply_text(help_text, parse_mode='Markdown')

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Действие отменено.",
        reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
    )
    return ConversationHandler.END

# --- Система пожеланий ---
def start_wishes(update: Update, context: CallbackContext):
    update.message.reply_text(
        "✏️ *Расскажите о ваших пожеланиях к подаркам*\n\n"
        "Опишите, что вам нравится, какие у вас интересы, "
        "что вы хотели бы получить в подарок:\n\n"
        "*Пример:*\n"
        "Люблю книги в жанре фэнтези, коллекционирую кружки, "
        "размер одежды M, аллергия на шоколад, мечтаю о настольной игре",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return WISHES

def save_wishes(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    wishes_text = update.message.text
    user_wishes[user_id] = wishes_text
    
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['📋 Мои игры', '✏️ Изменить пожелания', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "✅ *Ваши пожелания сохранены!*\n\n"
        "Когда вы будете распределены в игре, ваш Тайный Санта "
        "увидит эту информацию и сможет выбрать подарок, который вам точно понравится!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# --- Основные обработчики ---
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == '🎅 Создать игру':
        update.message.reply_text("🎅 Функция создания игры в разработке!")
    elif text == '🎄 Присоединиться к игре':
        update.message.reply_text("🎄 Функция присоединения в разработке!")
    elif text == '📋 Мои игры':
        update.message.reply_text("📋 Список игр в разработке!")
    elif text == '✏️ Мои пожелания' or text == '✏️ Изменить пожелания':
        update.message.reply_text("✏️ Функция пожеланий в разработке!")
    elif text == '❓ Помощь':
        help_command(update, context)
    else:
        update.message.reply_text(
            "Используйте кнопки меню или введите команду /start",
            reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text("🎅 Эта функция скоро будет доступна!")

# --- Главная функция ---
def main():
    print("🚀 Запуск бота Тайного Санты...")
    
    # Создаем Updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Получаем dispatcher для регистрации обработчиков
    dp = updater.dispatcher
    
    # Регистрируем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запускаем бота
    print("✅ Бот запущен и работает!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
