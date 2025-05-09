import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes
from services.politician_data import load_all_politicians
from services.user_state import get_user_state
from razdel import tokenize

politicians = load_all_politicians()


def split_text_into_pages(text: str, max_length: int = 1000):
    words = list(tokenize(text))
    pages = []
    current_page = ""

    for word in words:
        if len(current_page) + len(word.text) + 1 <= max_length:
            current_page += (word.text if current_page == "" else " " + word.text)
        else:
            pages.append(current_page)
            current_page = word.text

    if current_page:
        pages.append(current_page)

    return pages


async def send_paginated_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, action: str, page: int,
                              politician_name: str):
    pages = split_text_into_pages(text)
    total_pages = len(pages)

    kb_buttons = []
    if page > 0:
        kb_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{action}_page_{page - 1}"))
    if page < total_pages - 1:
        kb_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"{action}_page_{page + 1}"))
    kb_buttons.append(InlineKeyboardButton("🔙 В меню", callback_data="select_politician"))

    kb = InlineKeyboardMarkup([kb_buttons])

    await update.callback_query.message.delete()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{politician_name} — {action.upper()} (страница {page + 1}/{total_pages})*\n\n{pages[page]}",
        parse_mode="Markdown",
        reply_markup=kb
    )


# Функция для вывода ссылок в виде страниц
async def send_paginated_links(update: Update, context: ContextTypes.DEFAULT_TYPE, links: list, action: str, page: int,
                               politician_name: str):
    total_pages = len(links)

    kb_buttons = []
    if page > 0:
        kb_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{action}_page_{page - 1}"))
    if page < total_pages - 1:
        kb_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"{action}_page_{page + 1}"))
    kb_buttons.append(InlineKeyboardButton("🔙 В меню", callback_data="select_politician"))

    kb = InlineKeyboardMarkup([kb_buttons])

    await update.callback_query.message.delete()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{politician_name} — {action.upper()} (страница {page + 1}/{total_pages})*\n\n{links[page]}",
        parse_mode="Markdown",
        reply_markup=kb
    )


async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    index = get_user_state(user_id)
    politician = politicians[index]

    image_path = politician.get("image", "")
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(os.path.join(os.getcwd(), image_path))

    if not os.path.exists(image_path):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Фото не найдено.")
        return

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 История", callback_data="history")],
        [InlineKeyboardButton("🧠 Факты", callback_data="facts")],
        [InlineKeyboardButton("🔗 Ссылки", callback_data="links")],
        [InlineKeyboardButton("🎮 Начать игру", callback_data="start_game")],
        [InlineKeyboardButton("🔙 Назад", callback_data="choose_politician")]
    ])

    await update.callback_query.message.delete()

    with open(image_path, "rb") as f:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(f),
            caption=f"Что вы хотите узнать о {politician['name']}?",
            reply_markup=kb
        )


async def handle_menu_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    index = get_user_state(user_id)
    politician = politicians[index]
    action = update.callback_query.data

    if action == "start_game":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🎮 Игра ещё в разработке.")
    else:
        if action == "facts":
            facts = politician.get("facts", ["Факты не доступны."])
            await send_paginated_facts(update, context, facts, action, 0, politician["name"])
        elif action == "links":
            links = politician.get("links", ["Ссылки не доступны."])
            await send_paginated_links(update, context, links, action, 0, politician["name"])
        else:
            info = politician.get(action, "Информация пока недоступна.")
            await send_paginated_text(update, context, info, action, 0, politician["name"])

# Функция для вывода фактов в виде страниц
async def send_paginated_facts(update: Update, context: ContextTypes.DEFAULT_TYPE, facts: list, action: str, page: int,
                               politician_name: str):
    total_pages = len(facts)

    kb_buttons = []
    if page > 0:
        kb_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{action}_page_{page - 1}"))
    if page < total_pages - 1:
        kb_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"{action}_page_{page + 1}"))
    kb_buttons.append(InlineKeyboardButton("🔙 В меню", callback_data="select_politician"))

    kb = InlineKeyboardMarkup([kb_buttons])

    await update.callback_query.message.delete()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{politician_name} — {action.upper()} (страница {page + 1}/{total_pages})*\n\n{facts[page]}",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def handle_page_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.effective_user.id
    index = get_user_state(user_id)
    politician = politicians[index]

    parts = update.callback_query.data.split("_page_")
    action = parts[0]
    page = int(parts[1])

    if action == "facts":
        facts = politician.get("facts", ["Факты не доступны."])
        await send_paginated_facts(update, context, facts, action, page, politician["name"])
    elif action == "links":
        links = politician.get("links", ["Ссылки не доступны."])
        await send_paginated_links(update, context, links, action, page, politician["name"])
    else:
        info = politician.get(action, "Информация пока недоступна.")
        await send_paginated_text(update, context, info, action, page, politician["name"])


def register_handlers(app):
    app.add_handler(CallbackQueryHandler(handle_selection, pattern="^select_politician$"))
    app.add_handler(CallbackQueryHandler(handle_menu_action, pattern="^(history|facts|links|start_game)$"))
    app.add_handler(CallbackQueryHandler(handle_page_navigation, pattern="^(history|facts|links)_page_\\d+$"))
