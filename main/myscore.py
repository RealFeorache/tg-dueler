from telegram import Update
from telegram.ext import CallbackContext
from main.database import *
from main.helpers import record_user_chat_data
from main.duel import get_user_exp
from main.constants import DD


@db_session
def myscore(update: Update, context: CallbackContext):
    """Send the user his dueling score."""
    record_user_chat_data(update, context, update.message.from_user)
    u_data = Scores[Users[update.message.from_user.id],
                    Chats[update.message.chat.id]]
    exp = max(round(get_user_exp(update)*100, 2), DD['EXP_CAP'])
    text = ("K/D/A\n"
            f"{u_data.kills}/{u_data.deaths}/{u_data.misses}\n"
            f"Шанс победы увеличен на {exp}% (Макс = {DD['EXP_CAP']*100}%)")
    update.message.reply_text(text)
