import logging
from telegram.ext import ApplicationBuilder
import config
from handlers.start import register_handlers as start_handlers
from handlers.choose_politician import register_handlers as choose_handlers
from handlers.politician_menu import register_handlers as menu_handlers
from handlers.game_module import register_handlers as game_handlers


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    start_handlers(app)
    choose_handlers(app)
    menu_handlers(app)
    game_handlers(app)

    print('Bot started...')
    app.run_polling()

if __name__ == '__main__':
    main()