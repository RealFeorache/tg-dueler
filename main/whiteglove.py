"""Say hello."""
from telegram import Update, User
from telegram.ext import CallbackContext
from main.database import *


def whiteglove(update: Update, context: CallbackContext):
    """Call another user on a duel."""
    # Check if the target is valid
    objection = validity_check(update, context)
    if objection:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=objection,
            reply_to_message_id=update.message.message_id
        )
        return
    # Get initiator data and tag
    init_data = update.message.from_user
    init_tag = f'[{init_data.first_name}](tg://user?id={init_data.id})'
    # Get target data and tag
    targ_data = update.message.reply_to_message.from_user
    targ_tag = f'[{targ_data.first_name}](tg://user?id={targ_data.id})'
    # Record the duel call
    record_duel_call(update, context, init_data, targ_data)
    # Notify that the whiteglove call was successful
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f'{init_tag} вызвал {targ_tag} на дуэль!\n{targ_tag} теперь может использовать /duel на {init_tag}.',
        reply_to_message_id=update.message.message_id,
        parse_mode='Markdown'
    )


def validity_check(update: Update, context: CallbackContext):
    """Check if the whitegloved target is a valid one."""
    reply = ''
    # No choice
    if update.message.chat.type == 'private':
        reply = 'Бот-секундант работает только в группах.'
    elif update.message.reply_to_message is None:
        reply = 'Не выбран соперник. Чтобы выбрать, ответьте ему.'
    # Bot chosen
    elif update.message.reply_to_message.from_user.id == context.bot.id:
        reply = 'На секунданта нападать нельзя.'
    # Other bot chosen
    elif update.message.reply_to_message.from_user.is_bot:
        reply = 'Бота невозможно вызвать на дуэль'
    return reply


@db_session
def record_duel_call(update: Update, context: CallbackContext,
                     init_data: User, targ_data: User):
    """Record the duel call."""
    # Record the chat
    if not Chats.exists(id=update.message.chat.id):
        Chats(
            id=update.message.chat.id,
            title=update.message.chat.title or 'Private',
            link=update.message.chat.link or 'Private'
        )
    # Record the users
    for data in init_data, targ_data:
        if not Users.exists(id=data.id):
            Users(
                id=data.id,
                full_name=data.full_name,
                username=data.username or 'Unknown',
                link=data.link or 'Unknown',
            )
    # Record the target for the duel
    if not Scores.exists(
        user_id=Users[init_data.id],
        chat_id=Chats[update.message.chat.id]
    ):
        Scores(
            user_id=Users[init_data.id],
            chat_id=Chats[update.message.chat.id],
            target_id=Users[targ_data.id]
        )
    else:
        Scores[
            Users[init_data.id],
            Chats[update.message.chat.id]
        ].target_id = Users[targ_data.id]
