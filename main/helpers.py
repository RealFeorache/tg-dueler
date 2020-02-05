"""Helping function for the bot, not main ones."""
from telegram import Update
from telegram.ext import CallbackContext
from main.database import *


def validity_check(func):
    """Check for validity of the command.

    Checks for:
    1. If it's a group chat
    2. If a target for the command was chosen
    3. If this bot was the target
    4. If some bot was the target
    """
    def checker(update: Update, context: CallbackContext, *args, **kwargs):
        objection = ''
        # Not a group chat
        if update.message.chat.type == 'private':
            objection = 'Бот-секундант работает только в группах.'
        # No target
        elif update.message.reply_to_message is None:
            objection = 'Не выбран соперник. Чтобы выбрать, ответьте ему.'
        # Bot chosen
        elif update.message.reply_to_message.from_user.id == context.bot.id:
            objection = 'На секунданта нападать нельзя.'
        # Other bot chosen
        elif update.message.reply_to_message.from_user.is_bot:
            objection = 'Бота невозможно вызвать на дуэль.'
        if objection:
            context.bot.send_message(
                chat_id=update.message.chat.id,
                text=objection,
                reply_to_message_id=update.message.message_id
            )
            return
        record_user_chat_data(update, context)
        func(update, context, *args, **kwargs)

    return checker


@db_session
def record_user_chat_data(update: Update, context: CallbackContext):
    """Record the User and Chat data to the table."""
    init_data = update.message.from_user
    targ_data = update.message.reply_to_message.from_user
    # Record the chat
    if not Chats.exists(id=update.message.chat.id):
        Chats(
            id=update.message.chat.id,
            title=update.message.chat.title or 'Private',
            link=update.message.chat.link or 'Private'
        )
    # Record the users and scores
    for data in init_data, targ_data:
        if not Users.exists(
                id=data.id):
            Users(
                id=data.id,
                full_name=data.full_name,
                username=data.username or 'Unknown',
                link=data.link or 'Unknown',
            )
        if not Scores.exists(
                user_id=Users[data.id],
                chat_id=Chats[update.message.chat.id]):
            Scores(
                user_id=Users[data.id],
                chat_id=Chats[update.message.chat.id]
            )
