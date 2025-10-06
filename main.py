import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎅 *Добро пожаловать в Тайного Санту!*\n\n"
        "Бот успешно запущен и работает! 🚀\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
*🎅 Тайный Санта Бот*

🤖 *Бот работает исправно!*

*Доступные функции:*
✅ Главное меню
✅ Кнопки навигации  
✅ Обработка сообщений

*Скоро будут добавлены:*
🎅 Создание игр
🎄 Присоединение к играм
📋 Управление играми
✏️ Пожелания подарков

*Команды:*
/start - главное меню
/help - эта справка

*Приятной игры!* 🎄
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🎅 Создать игру':
        await update.message.reply_text(
            "🎅 *Создание игры*\n\n"
            "Функция создания игр будет доступна в ближайшем обновлении!",
            parse_mode='Markdown'
        )
    elif text == '🎄 Присоединиться к игре':
        await update.message.reply_text(
            "🎄 *Присоединение к игре*\n\n" 
            "Функция присоединения к играм будет доступна в ближайшем обновлении!",
            parse_mode='Markdown'
        )
    elif text == '❓ Помощь':
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "Используйте кнопки меню или введите /start",
            reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
        )

def main():
    print("=" * 50)
    print("🚀 ЗАПУСК БОТА ТАЙНОГО САНТЫ")
    print("=" * 50)
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не найден!")
        print("Проверьте переменные окружения")
        return
    
    print("✅ BOT_TOKEN найден")
    
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Бот инициализирован")
        print("🎅 Запускаю polling...")
        print("🤖 Бот готов к работе!")
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("💡 Попробуйте использовать Python 3.11")

if __name__ == '__main__':
    main()
