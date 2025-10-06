import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['📋 Мои игры', '✏️ Мои пожелания', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎅 *Добро пожаловать в Тайного Санту!*\n\n"
        "Я помогу вам организовать обмен подарками.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
*🎅 Как организовать Тайного Санту:*

1. *Создайте игру* - нажмите "🎅 Создать игру"
2. *Пригласите друзей* - поделитесь кодом комнаты  
3. *Проведите жеребьевку* - когда все готовы
4. *Обмен подарками!* - каждый узнает, кому дарить

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
            "Чтобы создать игру Тайного Санты:\n"
            "1. Придумайте название игры\n"
            "2. Установите бюджет подарков\n" 
            "3. Пригласите друзей по коду\n\n"
            "Эта функция скоро будет полностью доступна!",
            parse_mode='Markdown'
        )
    elif text == '🎄 Присоединиться к игре':
        await update.message.reply_text(
            "🎄 *Присоединение к игре*\n\n" 
            "Чтобы присоединиться к существующей игре:\n"
            "1. Получите код комнаты от организатора\n"
            "2. Введите код для присоединения\n"
            "3. Ожидайте начала жеребьевки\n\n"
            "Эта функция скоро будет полностью доступна!",
            parse_mode='Markdown'
        )
    elif text == '📋 Мои игры':
        await update.message.reply_text(
            "📋 *Мои игры*\n\n"
            "Здесь вы увидите все ваши активные игры Тайного Санты.\n\n"
            "Пока нет активных игр. Создайте новую игру!",
            parse_mode='Markdown'
        )
    elif text == '✏️ Мои пожелания':
        await update.message.reply_text(
            "✏️ *Мои пожелания*\n\n"
            "Расскажите о ваших предпочтениях в подарках:\n"
            "- Любимые жанры книг/фильмов\n" 
            "- Размер одежды/обуви\n"
            "- Хобби и интересы\n"
            "- Аллергии и ограничения\n\n"
            "Эта функция скоро будет доступна!",
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
    print("🚀 Запуск бота Тайного Санты...")
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не найден!")
        print("Установите переменную BOT_TOKEN в настройках Railway")
        return
    
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрируем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # Регистрируем обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запускаем бота
        print("✅ Бот успешно запущен!")
        print("🤖 Ожидаю сообщения...")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
