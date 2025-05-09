from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, CommandHandler

# Стартовое меню
async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Выбрать политика", callback_data="choose_politician")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")],  # Кнопка FAQ
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about_project")]  # Кнопка О проекте
    ])
    photo_path = "data/images/start.jpg"  # замените на нужный путь (относительный или абсолютный)

    # Определяем, откуда пришёл апдейт
    if update.message:
        await update.message.reply_photo(photo=open(photo_path, "rb"), reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.delete()
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(photo_path, "rb"),
            reply_markup=keyboard
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚫 Не удалось открыть стартовое меню."
        )

# Обработчик возврата в стартовое меню
async def return_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start_menu(update, context)

# Обработчик для FAQ
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()
    await update.callback_query.message.reply_text(
        "📚 FAQ:\n1. Как выбрать политика?\n2. Какие действия нужно сделать?"
    )

# Обработчик для информации о проекте
async def about_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.delete()
    await update.callback_query.message.reply_text(
        "ℹ️ О проекте:\nЭто проект, где вы можете выбрать историческую личность и узнать о её эпохе."
    )

# Регистрация хендлеров
def register_start_handlers(app):
    app.add_handler(CommandHandler("start", start_menu))
    app.add_handler(CallbackQueryHandler(return_to_start, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(faq, pattern="^faq$"))  # Регистрация кнопки FAQ
    app.add_handler(CallbackQueryHandler(about_project, pattern="^about_project$"))  # Регистрация кнопки О проекте
