from razdel import tokenize
from telegram import Message
from telegram.ext import ContextTypes

async def delete_previous_message(message: Message, context: ContextTypes.DEFAULT_TYPE = None):
    try:
        await message.delete()
    except Exception:
        pass


def split_text_into_pages(text: str, max_length: int = 800):
    words = list(tokenize(text))
    pages, current = [], ''
    for w in words:
        piece = w.text if not current else ' ' + w.text
        if len(current) + len(piece) > max_length:
            pages.append(current)
            current = w.text
        else:
            current += piece
    if current:
        pages.append(current)
    return pages