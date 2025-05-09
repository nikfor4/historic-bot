from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

user_game_states = {}

def create_choice_keyboard(choices, step_index):
    buttons = [
        [InlineKeyboardButton(choice["text"], callback_data=f"game:{step_index}:{i}")]
        for i, choice in enumerate(choices)
    ]
    return InlineKeyboardMarkup(buttons)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from services.politician_data import load_all_politicians
    politicians = load_all_politicians()
    index = 0  # заглушка, позже можно передавать через состояние
    politician = politicians[index]
    user_game_states[user_id] = {
        "politician": politician,
        "step": 0
    }
    await show_game_step(update, context, politician, 0)

async def show_game_step(update: Update, context: ContextTypes.DEFAULT_TYPE, politician: dict, step_index: int):
    step = politician["game"][step_index]
    kb = create_choice_keyboard(step["choices"], step_index)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{politician['name']} — ваш выбор:*\n\n{step['question']}",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def show_ending(update: Update, context: ContextTypes.DEFAULT_TYPE, ending_key: str, politician_name: str):
    endings = {
        "end_lenin_1": "Вы построили новое социалистическое государство.",
        "end_lenin_2": "Вы вызвали раскол в партии и потеряли поддержку."
    }
    text = endings.get(ending_key, "Конец игры.")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="start")]
    ])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{politician_name}*\n\n{text}",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def process_game_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    state = user_game_states.get(user_id)
    if not state:
        await update.callback_query.message.reply_text("Игра не найдена. Попробуйте заново.")
        return

    data = update.callback_query.data
    _, step_str, choice_index_str = data.split(":")
    step_index = int(step_str)
    choice_index = int(choice_index_str)

    politician = state["politician"]
    current_step = politician["game"][step_index]
    choice = current_step["choices"][choice_index]
    next_step = choice["next"]

    await update.callback_query.message.delete()

    if isinstance(next_step, int):
        user_game_states[user_id]["step"] = next_step
        await show_game_step(update, context, politician, next_step)
    elif isinstance(next_step, str) and next_step.startswith("end_"):
        await show_ending(update, context, next_step, politician["name"])
        user_game_states.pop(user_id, None)
    else:
        await update.callback_query.message.reply_text("Ошибка в сценарии. Обратитесь к разработчику.")

def register_handlers(app):
    app.add_handler(CallbackQueryHandler(start_game, pattern="^start_game$"))
    app.add_handler(CallbackQueryHandler(process_game_choice, pattern="^game:"))
