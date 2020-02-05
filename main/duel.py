"""Module responsible for duels."""
# TODO - Add dueling logic, EXP, cooldowns

from telegram import Update, User
from telegram.ext import CallbackContext
from main.helpers import validity_check
from main.database import *


@validity_check
def duel(update: Update, context: CallbackContext):
    """Duel the person if he has whitegloved you."""
    # Get users
    init_data = update.message.from_user
    targ_data = update.message.reply_to_message.from_user
    # Check if the target has whitegloved the initiator
    if not called_to_duel(update, init_data, targ_data):
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text='Этот пользователь не вызывал вас на дуэль.',
            reply_to_message_id=update.message.message_id
        )
        return


@db_session
def called_to_duel(update: Update, init_data: User, targ_data: User):
    """Check if the target has called the initiator onto a duel using /whiteglove."""
    if Scores.exists(
        user_id=Users[targ_data.id],
        chat_id=Chats[update.message.chat.id]
    ):
        if Scores[Users[targ_data.id], Chats[update.message.chat.id]].target_id \
                is Users[init_data.id]:
            return True
    return False
