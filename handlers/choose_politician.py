import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes
from services.politician_data import load_all_politicians
from services.user_state import get_user_state, set_user_state
from utils.message_utils import delete_previous_message

politicians = load_all_politicians()

async def show_politician(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    if update.callback_query and update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    pol = politicians[index]
    img_path = pol.get('image')
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Выбрать", callback_data="select_politician")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="prev_politician"),
         InlineKeyboardButton("➡️ Далее", callback_data="next_politician")],
        [InlineKeyboardButton("🔙 В начало", callback_data="start")]
    ])

    text = f"*{pol['name']}*"

    if img_path and os.path.exists(img_path):
        try:
            with open(img_path, 'rb') as img:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=img,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=kb
                )
                return
        except Exception as e:
            print(f"Error sending photo: {e}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown',
        reply_markup=kb
    )

async def handle_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    set_user_state(user_id, 0)
    await show_politician(update, context, 0)

async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    idx = get_user_state(user_id) or 0
    idx = (idx + (1 if update.callback_query.data == 'next_politician' else -1)) % len(politicians)
    set_user_state(user_id, idx)
    await show_politician(update, context, idx)

async def select_politician(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    from handlers.politician_menu import handle_selection
    await handle_selection(update, context)

def register_handlers(app):
    app.add_handler(CallbackQueryHandler(handle_choose,    pattern='^choose_politician$'))
    app.add_handler(CallbackQueryHandler(handle_navigation,pattern='^(next_politician|prev_politician)$'))
    app.add_handler(CallbackQueryHandler(select_politician,pattern='^select_politician$'))