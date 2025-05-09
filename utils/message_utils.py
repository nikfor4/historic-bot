# utils/message_utils.py

from telegram import Message
from telegram.ext import ContextTypes

async def delete_previous_message(message: Message, context: ContextTypes.DEFAULT_TYPE = None):
    try:
        await message.delete()
    except Exception:
        pass  # Сообщение уже удалено или не может быть удалено
