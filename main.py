from telegram.ext import Application, CallbackQueryHandler, CommandHandler
from handlers import start, choose_politician, politician_menu
from services import game_engine
from config import BOT_TOKEN

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Подключаем обработчики
    start.register_start_handlers(app)
    choose_politician.register_handlers(app)
    politician_menu.register_handlers(app)
    game_engine.register_handlers(app)

    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
