import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes
from services.politician_data import load_all_politicians
from services.user_state import get_user_state
from razdel import tokenize
# game_module.py

async def start_game(update, context, politician):
    # Запуск игры для политика
    question_index = 0
    await show_question(update, context, politician, question_index)


# Функция для показа вопроса в игре
async def show_question(update, context, politician, question_index):
    question = politician["game"][question_index]

    # Создание кнопок выбора
    kb_buttons = []
    for i, choice in enumerate(question["choices"]):
        kb_buttons.append(InlineKeyboardButton(choice["text"], callback_data=f"choice_{question_index}_{i}"))

    kb = InlineKeyboardMarkup([kb_buttons])

    # Отправка сообщения с вопросом и кнопками выбора
    await update.callback_query.message.delete()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{politician['name']} - Вопрос {question_index + 1}:*\n\n{question['question']}",
        parse_mode="Markdown",
        reply_markup=kb
    )


# Функция для обработки выбора пользователя в игре
async def handle_choice(update, context):
    await update.callback_query.answer()

    # Разбор данных из callback_data
    data = update.callback_query.data
    _, question_index, choice_index = data.split("_")

    question_index = int(question_index)
    choice_index = int(choice_index)

    politician = politicians[0]  # Берём первого политика (по умолчанию)
    question = politician["game"][question_index]
    choice = question["choices"][choice_index]

    # Отправка результата выбора
    await update.callback_query.message.delete()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*Результат выбора:*\n\n{choice['text']}\n\n{politician['name']} продолжает свою борьбу.",
        parse_mode="Markdown",
    )

    # Проверка, какой следующий шаг
    next_step = choice["next"]
    if isinstance(next_step, int):
        await show_question(update, context, politician, next_step)
    else:
        await end_game(update, context, next_step)


async def end_game(update, context, end_condition):
    if end_condition == "win":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Поздравляем! Вы выиграли игру!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Игра окончена.")
