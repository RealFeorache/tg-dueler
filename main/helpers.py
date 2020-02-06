"""Helping function for the bot, not main ones."""
from telegram import Update, Message
from telegram.ext import CallbackContext
from main.database import *
from datetime import timedelta


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
            update.message.reply_text(objection)
            return
        func(update, context, *args, **kwargs)

    return checker


@db_session
def record_user_chat_data(update: Update, context: CallbackContext, *users):
    """Record the User and Chat data to the table."""
    # Record the chat
    if not Chats.exists(id=update.message.chat.id):
        Chats(id=update.message.chat.id,
              title=update.message.chat.title or 'Private',
              link=update.message.chat.link or 'Private')
    # Record the users and scores
    for data in users:
        if not Users.exists(id=data.id):
            Users(id=data.id,
                  full_name=data.full_name,
                  username=data.username or 'Unknown',
                  link=data.link or 'Unknown')
        if not Scores.exists(user_id=Users[data.id],
                             chat_id=Chats[update.message.chat.id]):
            Scores(user_id=Users[data.id],
                   chat_id=Chats[update.message.chat.id])


def check_cooldown(func) -> Message:
    """Check if there is a cooldown for the duel for the user."""

    @db_session
    def cooldown(update: Update, context: CallbackContext, *args, **kwargs):
        record_user_chat_data(update, context,
                              update.message.from_user,
                              update.message.reply_to_message.from_user)
        last_duel = Scores[Users[update.message.from_user.id],
                           Chats[update.message.chat.id]].last_duel
        chat_cooldown = Chats[update.message.chat.id].duel_cooldown
        if last_duel is None or \
                last_duel < datetime.now() - timedelta(minutes=chat_cooldown):
            func(update, context, *args, **kwargs)
        else:
            remaining = last_duel + \
                timedelta(minutes=chat_cooldown) - datetime.now()
            update.message.reply_text(
                f'До вашей следующей инициации дуэли осталось {remaining.seconds} секунд.'
            )

    return cooldown


def admin_check(func) -> Message:
    """Check if the command came from the admin."""

    def checker(update: Update, context: CallbackContext, *args, **kwargs):
        admins = [
            u.user for u in context.bot.get_chat_administrators(
                chat_id=update.message.chat.id
            )
        ]
        if update.message.from_user in admins:
            func(update, context, *args, **kwargs)
        else:
            update.message.reply_text(
                'Эта команда только для администраторов.')

    return checker
