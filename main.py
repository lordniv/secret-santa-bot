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
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# --- Конфигурация ---
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    print("📝 Установите переменную BOT_TOKEN в настройках Railway")
    exit(1)

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['📋 Мои игры', '✏️ Мои пожелания', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
    )
    return ConversationHandler.END

# --- Система пожеланий ---
async def start_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
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

async def save_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    wishes_text = update.message.text
    user_wishes[user_id] = wishes_text
    
    keyboard = [
        ['🎅 Создать игру', '🎄 Присоединиться к игре'],
        ['📋 Мои игры', '✏️ Изменить пожелания', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "✅ *Ваши пожелания сохранены!*\n\n"
        "Когда вы будете распределены в игре, ваш Тайный Санта "
        "увидит эту информацию и сможет выбрать подарок, который вам точно понравится!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

# --- Создание комнаты ---
async def create_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎅 *Создание новой игры Тайного Санты*\n\n"
        "Как назовем вашу игру? (например: 'Семейный Новый Год' или 'Офисный обмен')",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return SETTING_NAME

async def set_room_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['room_name'] = update.message.text
    await update.message.reply_text(
        "📝 *Отлично!* Теперь опишите игру:\n"
        "(например: 'Обмен подарками в кругу семьи', 'Офисный Тайный Санта')\n"
        "Или просто нажмите /skip чтобы пропустить",
        parse_mode='Markdown'
    )
    return SETTING_DESCRIPTION

async def set_room_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['room_description'] = update.message.text
    return await ask_budget(update, context)

async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['room_description'] = "Без описания"
    return await ask_budget(update, context)

async def ask_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 *Укажите бюджет подарков:*\n"
        "(например: 1000 рублей, до 2000р, или 'без ограничений')\n"
        "Это поможет участникам ориентироваться в выборе подарка",
        parse_mode='Markdown'
    )
    return SETTING_BUDGET

async def set_room_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['room_budget'] = update.message.text
    await update.message.reply_text(
        "📅 *Когда планируете обмен подарками?*\n"
        "(например: '25 декабря', '30 декабря', 'Новый Год')\n"
        "Или нажмите /skip",
        parse_mode='Markdown'
    )
    return SETTING_DATE

async def set_room_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exchange_date'] = update.message.text
    return await finish_room_creation(update, context)

async def skip_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['exchange_date'] = "Дата не указана"
    return await finish_room_creation(update, context)

async def finish_room_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    room_code = generate_room_code()
    
    rooms[room_code] = {
        'name': context.user_data['room_name'],
        'description': context.user_data['room_description'],
        'budget': context.user_data['room_budget'],
        'date': context.user_data['exchange_date'],
        'admin': user_id,
        'participants': [user_id],
        'user_names': {user_id: user_name},
        'shuffled': False,
        'pairs': {},
        'created_at': datetime.now()
    }
    
    user_rooms[user_id] = room_code
    pending_registrations[room_code] = []
    
    room_info = f"""
🎅 *Игра создана!*

*Название:* {rooms[room_code]['name']}
*Описание:* {rooms[room_code]['description']}
*Бюджет:* {rooms[room_code]['budget']}
*Дата обмена:* {rooms[room_code]['date']}

*Код комнаты:* `{room_code}`

*Поделитесь этим кодом с друзьями, чтобы они могли присоединиться!*

*Участники (1):*
- {user_name}
    """
    
    keyboard = [
        [InlineKeyboardButton("🔗 Поделиться кодом", 
             url=f"https://t.me/share/url?url=Присоединяйся%20к%20моей%20игре%20Тайного%20Санты!%20Код:%20{room_code}")],
        [InlineKeyboardButton("👥 Начать жеребьевку", callback_data=f"shuffle_{room_code}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        room_info,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data.clear()
    return ConversationHandler.END

# --- Присоединение к игре ---
async def join_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎄 *Присоединение к игре*\n\n"
        "Введите код комнаты:",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )

async def join_room_with_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    room_code = update.message.text.upper().strip()
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    if room_code not in rooms:
        await update.message.reply_text(
            "❌ *Комната не найдена*\n"
            "Проверьте правильность кода и попробуйте еще раз.",
            parse_mode='Markdown'
        )
        return
    
    room = rooms[room_code]
    
    if user_id in room['participants']:
        await update.message.reply_text("✅ Вы уже участвуете в этой игре!", parse_mode='Markdown')
        return
    
    if room['shuffled']:
        await update.message.reply_text(
            "❌ *Жеребьевка в этой комнате уже завершена!*\n"
            "Присоединиться нельзя.",
            parse_mode='Markdown'
        )
        return
    
    if user_id not in pending_registrations[room_code]:
        pending_registrations[room_code].append(user_id)
    
    try:
        await context.bot.send_message(
            chat_id=room['admin'],
            text=f"🎅 *Новый участник!*\n\n"
                 f"*{user_name}* хочет присоединиться к игре '{room['name']}'\n\n"
                 f"Код комнаты: `{room_code}`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Принять", callback_data=f"accept_{room_code}_{user_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{room_code}_{user_id}")
            ]])
        )
    except Exception as e:
        logging.error(f"Не удалось уведомить администратора: {e}")
    
    await update.message.reply_text(
        "✅ *Запрос на участие отправлен!*\n"
        "Ожидайте подтверждения от организатора.",
        parse_mode='Markdown'
    )

# --- Обработка inline кнопок ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith('shuffle_'):
        room_code = data.replace('shuffle_', '')
        await start_shuffle(query, context, room_code)
    
    elif data.startswith('accept_'):
        parts = data.split('_')
        room_code, target_user_id = parts[1], int(parts[2])
        await accept_participant(query, context, room_code, target_user_id)
    
    elif data.startswith('reject_'):
        parts = data.split('_')
        room_code, target_user_id = parts[1], int(parts[2])
        await reject_participant(query, context, room_code, target_user_id)

async def accept_participant(query, context, room_code, target_user_id):
    if room_code not in rooms:
        await query.edit_message_text("❌ Комната не найдена")
        return
    
    room = rooms[room_code]
    
    if query.from_user.id != room['admin']:
        await query.answer("Только организатор может принимать участников!", show_alert=True)
        return
    
    if target_user_id in pending_registrations[room_code]:
        pending_registrations[room_code].remove(target_user_id)
    
    room['participants'].append(target_user_id)
    
    try:
        user_chat = await context.bot.get_chat(target_user_id)
        user_name = user_chat.first_name
        room['user_names'][target_user_id] = user_name
    except Exception as e:
        logging.error(f"Не удалось получить имя пользователя: {e}")
        user_name = "Участник"
        room['user_names'][target_user_id] = user_name
    
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"🎉 Вас приняли в игру '*{room['name']}*'!\n\n"
                 f"Ожидайте начала жеребьевки.\n\n"
                 f"*Не забудьте указать ваши пожелания к подаркам!*",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Не удалось уведомить участника: {e}")
    
    participants_list = "\n".join([f"- {name}" for name in room['user_names'].values()])
    
    await query.edit_message_text(
        f"✅ Участник принят!\n\n"
        f"*Текущие участники ({len(room['participants'])}):*\n{participants_list}\n\n"
        f"Код комнаты: `{room_code}`",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🎲 Начать жеребьевку", callback_data=f"shuffle_{room_code}")
        ]])
    )

async def reject_participant(query, context, room_code, target_user_id):
    if room_code not in rooms:
        await query.edit_message_text("❌ Комната не найдена")
        return
    
    room = rooms[room_code]
    
    if query.from_user.id != room['admin']:
        await query.answer("Только организатор может отклонять участников!", show_alert=True)
        return
    
    if target_user_id in pending_registrations[room_code]:
        pending_registrations[room_code].remove(target_user_id)
    
    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"❌ К сожалению, организатор отклонил вашу заявку на участие в игре '*{room['name']}*'.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Не удалось уведомить участника: {e}")
    
    await query.edit_message_text("❌ Участник отклонен.")

async def start_shuffle(query, context, room_code):
    if room_code not in rooms:
        await query.edit_message_text("❌ Комната не найдена")
        return
    
    room = rooms[room_code]
    
    if query.from_user.id != room['admin']:
        await query.answer("Только организатор может начинать жеребьевку!", show_alert=True)
        return
    
    if len(room['participants']) < 2:
        await query.answer("Нужно как минимум 2 участника!", show_alert=True)
        return
    
    pairs = shuffle_participants(room['participants'])
    room['pairs'] = dict(pairs)
    room['shuffled'] = True
    
    successful_sends = 0
    for santa_id, receiver_id in pairs:
        santa_name = room['user_names'][santa_id]
        receiver_name = room['user_names'][receiver_id]
        
        receiver_wishes = user_wishes.get(receiver_id, "❓ *Пожелания не указаны*\n\nЭтот участник еще не рассказал о своих предпочтениях.")
        
        try:
            message_text = f"🎅 *Тайный Санта!*\n\n"
            message_text += f"Вы дарите подарок: *{receiver_name}*\n\n"
            message_text += f"*Пожелания получателя:*\n{receiver_wishes}\n\n"
            message_text += f"*Детали игры:*\n"
            message_text += f"- Название: {room['name']}\n"
            message_text += f"- Бюджет: {room['budget']}\n"
            message_text += f"- Дата обмена: {room['date']}\n\n"
            message_text += f"*Не говорите никому, кому вы дарите!* 🤫"
            
            await context.bot.send_message(
                chat_id=santa_id,
                text=message_text,
                parse_mode='Markdown'
            )
            successful_sends += 1
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {santa_id}: {e}")
    
    await query.edit_message_text(
        f"🎉 *Жеребьевка завершена!*\n\n"
        f"Сообщения отправлены {successful_sends} из {len(room['participants'])} участников.\n"
        f"Каждый знает, кому он дарит подарок и видит пожелания получателя.\n\n"
        f"*Участников:* {len(room['participants'])}\n"
        f"*Игра:* {room['name']}",
        parse_mode='Markdown'
    )

# --- Просмотр моих игр ---
async def my_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    user_games = []
    
    for room_code, room in rooms.items():
        if user_id in room['participants']:
            status = "👑 Организатор" if user_id == room['admin'] else "🎅 Участник"
            shuffle_status = "✅ Завершена" if room['shuffled'] else "⏳ Ожидание"
            
            user_games.append(
                f"*{room['name']}*\n"
                f"Код: `{room_code}` - {status}\n"
                f"Участников: {len(room['participants'])} - Жеребьевка: {shuffle_status}\n"
            )
    
    if not user_games:
        await update.message.reply_text(
            "У вас пока нет активных игр.\n"
            "Создайте новую игру или присоединитесь к существующей!",
            parse_mode='Markdown'
        )
        return
    
    games_text = "🎄 *Ваши игры:*\n\n" + "\n".join(user_games)
    await update.message.reply_text(games_text, parse_mode='Markdown')

# --- Обработка текстовых сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🎅 Создать игру':
        await create_room_start(update, context)
    elif text == '🎄 Присоединиться к игре':
        await join_room_start(update, context)
    elif text == '📋 Мои игры':
        await my_games(update, context)
    elif text == '✏️ Мои пожелания' or text == '✏️ Изменить пожелания':
        await start_wishes(update, context)
    elif text == '❓ Помощь':
        await help_command(update, context)
    else:
        if len(text.strip()) == 6 and text.strip().isalnum():
            await join_room_with_code(update, context)
        else:
            await update.message.reply_text(
                "Используйте кнопки меню или введите команду /start",
                reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
            )

# --- Главная функция ---
def main():
    print("🚀 Запуск бота Тайного Санты на Railway...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчик создания комнаты
    creation_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🎅 Создать игру$'), create_room_start)],
        states={
            SETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_room_name)],
            SETTING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_room_description),
                CommandHandler('skip', skip_description)
            ],
            SETTING_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_room_budget)],
            SETTING_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_room_date),
                CommandHandler('skip', skip_date)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Обработчик пожеланий
    wishes_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(✏️ Мои пожелания|✏️ Изменить пожелания)$'), start_wishes)],
        states={
            WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_wishes)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(creation_conv)
    application.add_handler(wishes_conv)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Regex('^📋 Мои игры$'), my_games))
    application.add_handler(MessageHandler(filters.Regex('^❓ Помощь$'), help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и работает на Railway!")
    print("🎅 Бот готов к использованию в Telegram!")
    application.run_polling()

if __name__ == '__main__':
    main()
