"""Commands for group admins."""
from telegram import Update, Message
from telegram.ext import CallbackContext
from main.database import *
from main.helpers import admin_check, record_user_chat_data


@admin_check
@db_session
def set_duel_cooldown(update: Update, context: CallbackContext) -> Message:
    """Set the duel cooldown for the chat."""
    record_user_chat_data(update, context, update.message.from_user)
    try:
        new_cooldown = int(update.message.text.split()[1])
        Chats[update.message.chat.id].duel_cooldown = new_cooldown
        reply = ('Новая задержка между дуэлями установлена.\n'
                 f'Теперь задержка {new_cooldown} минут.')
    except (IndexError, ValueError):
        reply = 'Неправильно использована команда.\nПример: /setduelcooldown 10'
    update.message.reply_text(reply)
