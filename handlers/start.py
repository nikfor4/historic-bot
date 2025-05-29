from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from utils.message_utils import delete_previous_message


# Стартовое меню
async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Удаляем предыдущее
    if update.message:
        await delete_previous_message(update.message, context)
    elif update.callback_query:
        await delete_previous_message(update.callback_query.message, context)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Выбрать политика", callback_data="choose_politician")],
        [InlineKeyboardButton("🏆 Достижения", callback_data="achievements")],
        [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about_project")]
    ])
    photo_path = os.path.join('data', 'images', 'start.jpg')

    # Отправляем меню
    if update.message:
        await update.message.reply_photo(photo=open(photo_path, 'rb'), reply_markup=keyboard)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(photo_path, 'rb'),
                                     reply_markup=keyboard)


# Возврат в стартовое меню
async def return_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start_menu(update, context)


# FAQ и О проекте
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await delete_previous_message(update.callback_query.message, context)
    text = (
        "📚 *FAQ — Часто задаваемые вопросы:*\n\n"
        "1️⃣ *Как выбрать политика?*\n"
        "Выбор политика осуществляется в начале игры. После запуска бота вы увидите список доступных исторических личностей — например, Ленина, Сталина, Ельцина и других. Просто нажмите на имя интересующего вас политика, и игра начнётся с вводной сцены, связанной с его эпохой. Каждый политик имеет уникальный сюжет и события, соответствующие реальной истории.\n\n"
        "2️⃣ *Какие действия доступны в игре?*\n"
        "В ходе игры вы будете сталкиваться с важными историческими событиями. На каждом этапе вы получаете текстовую сцену с описанием ситуации и два (или более) варианта выбора. Ваши решения влияют на дальнейшее развитие сюжета, параметры государства (в будущем будут вводиться переменные, такие как доверие народа, экономика и стабильность) и конечный исход истории. Также вы будете видеть иллюстрации и исторические справки по ходу игры.\n\n"
        "3️⃣ *Можно ли переиграть игру?*\n"
        "Да! Вы можете переигрывать игру сколько угодно раз, выбирая других политиков или принимая иные решения. Это поможет вам лучше понять, как альтернативные действия могли бы повлиять на ход истории.\n\n"
        "4️⃣ *Насколько достоверна информация в игре?*\n"
        "Мы стремимся к исторической точности. Каждый сюжет основан на реальных событиях, а в конце прохождения вы получаете краткую справку о том, как всё происходило на самом деле. В разделе с каждым политиком есть ссылки на проверенные источники — от научных статей до Википедии и просветительских платформ вроде Arzamas.\n\n"
        "5️⃣ *Можно ли предложить своего политика или сюжет?*\n"
        "Да! Мы рады обратной связи. Если у вас есть идея для нового персонажа или исторического сценария, напишите мне в телеграм [@Nikfor4]."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 В начало", callback_data="start")]
    ])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def about_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await delete_previous_message(update.callback_query.message, context)
    text = (
        "ℹ️ *О проекте:*\n\n"
        "🎮 _История становится игрой, а великие личности — вашими персонажами._\n\n"
        "Этот проект — интерактивный Telegram-бот, в котором вы играете за известных исторических деятелей России. В отличие от классических тестов и сухих фактов, здесь вы попадаете внутрь истории: делаете важнейшие политические выборы, сталкиваетесь с реальными вызовами и ведёте страну к разным исходам в зависимости от своих решений.\n\n"
        "📜 Каждый политик — это уникальный сюжет, созданный на основе реальных исторических событий. Например, играя за Ленина, вы решаете судьбу НЭПа и революции; играя за Сталина — запускаете индустриализацию и решаете, как справляться с внутренними угрозами. В конце каждого сценария даётся _историческая справка_, рассказывающая, как всё происходило в реальности.\n\n"
        "📸 Сцены сопровождаются изображениями и иллюстрациями для создания атмосферы и погружения в эпоху. А факты и ссылки, встроенные в профиль каждого персонажа, позволяют изучать материал глубже: мы используем проверенные источники (например, Википедию, Arzamas, «ПроЖито», РГАКФД и другие).\n\n"
        "📚 _Цель проекта_ — сделать изучение истории России не только познавательным, но и интерактивным. Это не просто образовательная игра, а способ «поиграть в альтернативную историю» и ощутить на себе, как сложно принимать решения на высшем уровне власти.\n\n"
        "🔁 Каждый выбор влияет на развитие событий. В будущем мы планируем внедрить переменные (например, уровень поддержки народа, политическую стабильность и экономику), а также развивать нелинейные ветвления, добавлять новые эпохи и персонажей — от императоров до реформаторов и современных лидеров.\n\n"
        "👥 *Разработчики проекта:*\n"
        "• Никифоров Кирилл [@Nikfor4]\n"
        "• Вольнова Анна\n"
        "• Николенко Максим\n\n"
        "📬 Хотите внести вклад? Мы открыты к предложениям: присылайте свои идеи по новым персонажам, сценариям или улучшениям игрового процесса. Этот проект развивается благодаря интересу и обратной связи от пользователей.\n\n"
        "*Сыграйте в историю — она уже началась.*"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 В начало", callback_data="start")]
    ])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# Регистрация
import os


def register_handlers(app):
    app.add_handler(CommandHandler('start', start_menu))
    app.add_handler(CallbackQueryHandler(return_to_start, pattern='^start$'))
    app.add_handler(CallbackQueryHandler(faq, pattern='^faq$'))
    app.add_handler(CallbackQueryHandler(about_project, pattern='^about_project$'))