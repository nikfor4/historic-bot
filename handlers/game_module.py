import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes
from services.politician_data import load_all_politicians
from services.user_state import get_user_state, clear_user_state
from utils.message_utils import delete_previous_message

user_games = {}

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if update.callback_query.message:
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

    if update.callback_query and update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(c['text'], callback_data=f"choice|{key}|{i}")]
        for i, c in enumerate(step.get('choices', []))
    ])

    img_path = step.get('image') or pol.get('image')
    caption = f"*{pol['name']} — {step.get('text', '')}*"

    if img_path and os.path.exists(img_path):
        try:
            with open(img_path, 'rb') as img:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=kb
                )
                return
        except Exception as e:
            print(f"Error sending photo: {e}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=caption,
        parse_mode='Markdown',
        reply_markup=kb
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    user_id = update.effective_user.id
    _, key, idx_s = update.callback_query.data.split('|')
    choice_idx = int(idx_s)

    pol_idx = get_user_state(user_id) or 0
    pol = load_all_politicians()[pol_idx]
    choice = pol['game'][key]['choices'][choice_idx]
    next_key = choice['next']

    if not (isinstance(next_key, str) and next_key.startswith('end_')):
        user_games[user_id] = str(next_key)
        await ask_question(update, context, pol, str(next_key))
        return

    # Финал
    end = pol['game'].get(next_key, {})
    end_text = end.get('text', 'Конец игры.')
    kb = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 В меню', callback_data='choose_politician')]])
    img_path = end.get('image') or pol.get('image')
    caption = f"*{pol['name']} — Игра окончена*\n\n{end_text}"

    if img_path and os.path.exists(img_path):
        try:
            with open(img_path, 'rb') as img:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=kb
                )
                clear_user_state(user_id)
                user_games.pop(user_id, None)
                return
        except Exception as e:
            print(f"Error sending photo: {e}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=caption,
        parse_mode='Markdown',
        reply_markup=kb
    )
    clear_user_state(user_id)
    user_games.pop(user_id, None)

def register_handlers(app):
    app.add_handler(CallbackQueryHandler(start_game, pattern='^start_game$'))
    app.add_handler(CallbackQueryHandler(handle_choice, pattern='^choice\\|'))