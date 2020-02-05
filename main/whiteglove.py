"""Say hello."""
from telegram import Update, User, Message
from telegram.ext import CallbackContext
from main.helpers import validity_check
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
    # Add the duel call
    Scores[
        Users[init_data.id],
        Chats[update.message.chat.id]
    ].target_id = Users[targ_data.id]
    # Notify that the whiteglove call was successful
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f'{init_tag} вызвал {targ_tag} на дуэль!\n{targ_tag} теперь может использовать /duel на {init_tag}.',
        reply_to_message_id=update.message.message_id,
        parse_mode='Markdown'
    )
