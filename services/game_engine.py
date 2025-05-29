# handlers/game_module.py

import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes
from services.politician_data import load_all_politicians
from services.user_state import get_user_state, clear_user_state
from utils.message_utils import delete_previous_message

# Храним состояние игр
user_games = {}

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # удаляем меню политика
    await delete_previous_message(update.callback_query.message, context)

    user_id = update.effective_user.id
    idx = get_user_state(user_id) or 0
    pol = load_all_politicians()[idx]

    user_games[user_id] = 'start'
    await ask_question(update, context, pol, 'start')

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, pol: dict, key: str):
    step = pol['game'].get(key)
    if not step:
        return

    # удаляем предыдущий вопрос/финал
    if update.callback_query:
        await delete_previous_message(update.callback_query.message, context)

    # собираем кнопки
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(choice['text'], callback_data=f"choice|{key}|{i}")]
        for i, choice in enumerate(step.get('choices', []))
    ])

    # пытаемся отправить фото
    img_path = step.get('image') or pol.get('image')
    if img_path and os.path.exists(img_path):
        try:
            with open(img_path, 'rb') as img_f:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=InputFile(img_f),
                    caption=f"*{pol['name']} — {step.get('text', '')}*",
                    parse_mode="Markdown",
                    reply_markup=kb
                )
            return
        except Exception:
            # если упало — упадём в текстовый fallback
            pass

    # fallback: текст + клавиатура
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{pol['name']} — {step.get('text', '')}*",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # удаляем сообщение с кнопками
    await delete_previous_message(update.callback_query.message, context)

    user_id = update.effective_user.id
    _, key, idx_str = update.callback_query.data.split('|')
    choice_idx = int(idx_str)

    pol_idx = get_user_state(user_id) or 0
    pol = load_all_politicians()[pol_idx]
    choice = pol['game'][key]['choices'][choice_idx]
    next_key = choice['next']

    # если следующий — это индекс шага
    if isinstance(next_key, int) or (isinstance(next_key, str) and not next_key.startswith('end_')):
        user_games[user_id] = str(next_key)
        await ask_question(update, context, pol, str(next_key))
    else:
        # финал
        end = pol['game'].get(next_key, {})
        text = end.get('text', 'Конец игры.')
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 В меню", callback_data="choose_politician")]
        ])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"*{pol['name']} — Игра окончена*\n\n{text}",
            parse_mode="Markdown",
            reply_markup=kb
        )
        user_games.pop(user_id, None)
        clear_user_state(user_id)

def register_handlers(app):
    app.add_handler(CallbackQueryHandler(start_game, pattern=r"^start_game$"))
    app.add_handler(CallbackQueryHandler(handle_choice, pattern=r"^choice\\|"))
