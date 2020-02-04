"""Say hello."""
from telegram import Update, User
from telegram.ext import CallbackContext
import main.helpers


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


@main.helpers.db_session
def record_duel_call(update: Update, context: CallbackContext,
                     init_data: User, targ_data: User):
    """Record the duel call."""
    # Record the chat
    if not main.helpers.Chats.exists(id=update.message.chat.id):
        main.helpers.Chats(
            id=update.message.chat.id,
            title=update.message.chat.title if update.message.chat.title else 'Private',
            link=update.message.chat.link if update.message.chat.link else 'Private'
        )
    # Record the users
    for data in init_data, targ_data:
        if not main.helpers.Users.exists(id=data.id):
            main.helpers.Users(
                id=data.id,
                full_name=data.full_name,
                username=data.username if data.username else 'Unknown',
                link=data.link if data.link else 'Unknown',
            )
    # Record the target for the duel
    if not main.helpers.Scores.exists(
        user_id=main.helpers.Users[init_data.id].id,
        chat_id=main.helpers.Chats[update.message.chat.id].id
    ):
        main.helpers.Scores(
            user_id=main.helpers.Users[init_data.id].id,
            chat_id=main.helpers.Chats[update.message.chat.id].id,
            target_id=main.helpers.Users[targ_data.id].id
        )
    else:
        pass
