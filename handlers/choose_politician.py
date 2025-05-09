import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes
from services.politician_data import load_all_politicians
from services.user_state import get_user_state, set_user_state  # Импортируем функции для работы с состоянием

politicians = load_all_politicians()

def build_keyboard(index: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Выбрать", callback_data="select_politician")],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="prev_politician"),
            InlineKeyboardButton("➡️ Далее", callback_data="next_politician")
        ],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="start")]
    ])

async def show_politician(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    politician = politicians[index]
    name = politician["name"]
    image_path = politician.get("image", "")

    if not os.path.isabs(image_path):
        image_path = os.path.abspath(os.path.join(os.getcwd(), image_path))

    logging.info(f"Загружается изображение для '{name}': {image_path}")

    if not os.path.exists(image_path):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Изображение не найдено.")
        return

    try:
        with open(image_path, "rb") as f:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=InputFile(f),
                caption=f"*{name}*\n\nВыберите, что делать.",
                parse_mode="Markdown",
                reply_markup=build_keyboard(index)
            )
    except Exception as e:
        logging.exception("Ошибка при отправке изображения")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Не удалось отправить изображение.")

async def handle_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    index = get_user_state(user_id)  # Используем функцию get_user_state для получения текущего состояния
    if index is None:
        index = 0  # Если состояние не найдено, начинаем с первого политика
    await show_politician(update, context, index)

async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    current_index = get_user_state(user_id)  # Получаем текущий индекс

    if current_index is None:
        current_index = 0  # Если индекс не установлен, начинаем с первого политика

    if update.callback_query.data == "next_politician":
        new_index = (current_index + 1) % len(politicians)
    else:
        new_index = (current_index - 1) % len(politicians)

    set_user_state(user_id, new_index)  # Обновляем состояние пользователя
    await show_politician(update, context, new_index)

def register_handlers(app):
    app.add_handler(CallbackQueryHandler(handle_choose, pattern="^choose_politician$"))
    app.add_handler(CallbackQueryHandler(handle_navigation, pattern="^(next_politician|prev_politician)$"))
