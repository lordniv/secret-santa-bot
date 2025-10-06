import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

def start(update: Update, context: CallbackContext):
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['📋 Мои игры', '✏️ Мои пожелания', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🎅 *Добро пожаловать в Тайного Санту!*\n\n"
        "🤖 *Бот успешно запущен и работает!*\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext):
    help_text = """
*🎅 Тайный Санта Бот*

✅ *Бот работает исправно!*

*Доступные функции:*
🎅 Главное меню
🎄 Навигация по кнопкам  
📋 Базовая функциональность

*Скоро будут добавлены:*
• Создание игр
• Присоединение к играм
• Жеребьевка
• Система пожеланий

*Команды:*
/start - главное меню
/help - эта справка

*Приятной игры!* 🎄
    """
    update.message.reply_text(help_text, parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == '🎅 Создать игру':
        update.message.reply_text(
            "🎅 *Создание игры*\n\n"
            "Функция будет доступна в следующем обновлении!\n"
            "Следите за новостями 🎄",
            parse_mode='Markdown'
        )
    elif text == '🎄 Присоединиться к игре':
        update.message.reply_text(
            "🎄 *Присоединение к игре*\n\n" 
            "Функция будет доступна в следующем обновлении!\n"
            "Следите за новостями 🎁",
            parse_mode='Markdown'
        )
    elif text == '📋 Мои игры':
        update.message.reply_text(
            "📋 *Мои игры*\n\n"
            "Функция будет доступна в следующем обновлении!",
            parse_mode='Markdown'
        )
    elif text == '✏️ Мои пожелания':
        update.message.reply_text(
            "✏️ *Мои пожелания*\n\n"
            "Функция будет доступна в следующем обновлении!",
            parse_mode='Markdown'
        )
    elif text == '❓ Помощь':
        help_command(update, context)
    else:
        update.message.reply_text(
            "Используйте кнопки меню или введите /start",
            reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )

def main():
    print("=" * 50)
    print("🚀 ЗАПУСК БОТА ТАЙНОГО САНТЫ")
    print("=" * 50)
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не найден!")
        print("Проверьте переменные окружения в Railway")
        return
    
    print("✅ BOT_TOKEN найден")
    
    try:
        # Создаем Updater (старый стиль, но стабильный)
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # Получаем диспетчер
        dp = updater.dispatcher
        
        # Регистрируем обработчики
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        print("✅ Бот инициализирован")
        print("🎅 Запускаю polling...")
        
        # Запускаем бота
        updater.start_polling()
        print("🤖 Бот успешно запущен и работает!")
        print("💫 Ожидаю сообщения...")
        
        # Бот работает пока не остановим
        updater.idle()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
