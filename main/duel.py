"""Module responsible for duels."""
# TODO - Cooldowns, duel outcome recording

from telegram import Update, User, Message
from telegram.ext import CallbackContext
from main import randomizer
from main.helpers import validity_check
from main.database import *
from main.constants import DD


@validity_check
def duel(update: Update, context: CallbackContext) -> Message:
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
    # Proceed to the duel
    win_threshold = randomizer.uniform(0, DD['WIN_ROLL_CAP'])
    init_roll = get_win_chance(update, init_data)
    targ_roll = get_win_chance(update, targ_data)
    # Duel outcomes message
    outcome_storer = {
        'init': {
            'user': init_data,
            'score': (,)
        }
        'targ': {
            'user': targ_data,
            'score': (,)
        }
    }
    if init_roll < win_threshold and targ_roll < win_threshold:
        duel_result = 'BOTH MISSED MESSAGE'
        outcome_storer['init']['score'] = (0, 0, 1)
        outcome_storer['targ']['score'] = (0, 0, 1)
    elif init_roll > win_threshold and targ_roll > win_threshold:
        duel_result = 'KILLED EACH OTHER MESSAGE'
        outcome_storer['init']['score'] = (1, 1, 0)
        outcome_storer['targ']['score'] = (1, 1, 0)
    elif init_roll > win_threshold:
        duel_result = 'INIT KILLED TARGET MESSAGE'
        outcome_storer['init']['score'] = (1, 0, 0)
        outcome_storer['targ']['score'] = (0, 1, 0)
    elif targ_roll > win_threshold:
        duel_result = 'TARG KILLED INIT MESSAGE'
        outcome_storer['init']['score'] = (0, 1, 0)
        outcome_storer['targ']['score'] = (1, 0, 0)
    # Record outcome
    record_outcome(outcome_storer)
    # Result message
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=duel_result,
        reply_to_message_id=update.message.message_id
    )


@db_session
def called_to_duel(update: Update, init_data: User, targ_data: User) -> bool:
    """Check if the target has called the initiator onto a duel using /whiteglove."""
    if Scores.exists(
        user_id=Users[targ_data.id],
        chat_id=Chats[update.message.chat.id]
    ):
        if Scores[Users[targ_data.id], Chats[update.message.chat.id]].target_id \
                is Users[init_data.id]:
            return True
    return False


@db_session
def get_win_chance(update: Update, user_data: User) -> float:
    """Get the win chance of a user, accounting for the experience."""
    win_roll = randomizer.uniform(0, DD['RANDOM_ROLL_CAP'])
    if Scores.exists(
        user_id=Users[user_data.id],
        chat_id=Chats[update.message.chat.id]
    ):
        user_score = Scores[Users[user_data.id], Chats[update.message.chat.id]]
        win_roll += (user_score.kills * DD['KILL_EXP'] +
                     user_score.deaths * DD['DEATH_EXP'] +
                     user_score.misses * DD['MISS_EXP'])
    return win_roll


@db_session
def record_outcome(outcome_storer: dict) -> None:
    """Record the outcome in the database"""
    pass
