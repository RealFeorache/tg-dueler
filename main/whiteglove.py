"""Basically, a call for a duel."""
from telegram import Update, User, Message
from telegram.ext import CallbackContext
from main.helpers import validity_check, record_user_chat_data
from main.database import *


@validity_check
@db_session
def whiteglove(update: Update, context: CallbackContext) -> Message:
    """Call another user on a duel."""
    # Get initiator data and tag
    init_data = update.message.from_user
    init_tag = f'[{init_data.first_name}](tg://user?id={init_data.id})'
    # Get target data and tag
    targ_data = update.message.reply_to_message.from_user
    targ_tag = f'[{targ_data.first_name}](tg://user?id={targ_data.id})'
    record_user_chat_data(update, context, init_data, targ_data)
    # Add the duel call to the database
    Scores[Users[init_data.id], Chats[update.message.chat.id]].target_id = \
        Users[targ_data.id]
    # Notify that the whiteglove call was successful
    update.message.reply_text(
        text=(f'{init_tag} вызвал {targ_tag} на дуэль!\n'
              f'{targ_tag} теперь может использовать /duel на {init_tag}.'),
        parse_mode='Markdown'
    )
