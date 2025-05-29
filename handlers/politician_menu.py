import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import CallbackQueryHandler, ContextTypes, ApplicationBuilder
from services.politician_data import load_all_politicians
from services.user_state import get_user_state
from utils.message_utils import delete_previous_message, split_text_into_pages

# Загружаем данные политиков
politicians = load_all_politicians()

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # Удаляем предыдущее сообщение (это меню после выбора политика)
    if update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    user_id = update.effective_user.id
    idx = get_user_state(user_id) or 0
    pol = politicians[idx]

    # Формируем клавиатуру основного меню политика
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton('📖 История',    callback_data='history')],
        [InlineKeyboardButton('🧠 Факты',      callback_data='facts')],
        [InlineKeyboardButton('🏆 Достижения', callback_data='achievements')],
        [InlineKeyboardButton('🔗 Ссылки',     callback_data='links')],
        [InlineKeyboardButton('🎮 Начать игру', callback_data='start_game')],
        [InlineKeyboardButton('🔙 Назад',       callback_data='choose_politician')],
    ])

    # Если есть изображение, отправляем его с подписью
    img_path = pol.get('image')
    text = f"*{pol['name']} — Меню*"
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

    # Иначе текстовым сообщением
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown',
        reply_markup=kb
    )

async def handle_menu_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # Удаляем меню политика перед показом выбранного раздела
    if update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    user_id = update.effective_user.id
    idx = get_user_state(user_id) or 0
    pol = politicians[idx]
    action = update.callback_query.data

    # Навигация между экранами
    if action == 'choose_politician':
        from handlers.choose_politician import show_politician
        await show_politician(update, context, idx)
        return
    if action == 'start_game':
        from handlers.game_module import start_game
        await start_game(update, context)
        return

    # Готовим контент и разбиваем на страницы
    content = pol.get(action)
    pages = content if isinstance(content, list) \
        else split_text_into_pages(content or 'Информация недоступна.')
    context.user_data['pages'] = pages
    context.user_data['page_action'] = action
    context.user_data['pol_name'] = pol['name']

    # Отправляем первую страницу
    await send_page(update, context, 0)

async def send_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    # При пагинации тоже надо удалить текущее сообщение
    if update.callback_query and update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    pages = context.user_data['pages']
    action = context.user_data['page_action']
    name = context.user_data['pol_name']
    total = len(pages)

    # Навигационные кнопки
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton('⬅️ Назад', callback_data=f'{action}_page_{page-1}'))
    if page < total - 1:
        buttons.append(InlineKeyboardButton('➡️ Далее', callback_data=f'{action}_page_{page+1}'))
    buttons.append(InlineKeyboardButton('🔙 Меню', callback_data='select_politician'))

    # Отправляем текст текущей страницы
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"*{name} — {action.upper()} " 
            f"({page+1}/{total})*\n\n{pages[page]}"
        ),
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([buttons])
    )

async def handle_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    # Удаляем предыдущее сообщение перед отправкой новой страницы
    if update.callback_query.message:
        await delete_previous_message(update.callback_query.message, context)

    # Разбираем callback_data вида "history_page_2"
    _, page_str = update.callback_query.data.rsplit('_', 1)
    await send_page(update, context, int(page_str))

def register_handlers(app):
    app.add_handler(CallbackQueryHandler(handle_selection,    pattern='^select_politician$'))
    app.add_handler(CallbackQueryHandler(handle_menu_action,  pattern='^(history|facts|achievements|links|start_game|choose_politician)$'))
    app.add_handler(CallbackQueryHandler(handle_page,         pattern='^(history|facts|achievements|links)_page_\\d+$'))