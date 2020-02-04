"""Helping function for the bot, not main ones."""
from telegram import Update
from telegram.ext import CallbackContext


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
        func(update, context, *args, **kwargs)

    return checker
