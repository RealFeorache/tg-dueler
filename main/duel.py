"""Module responsible for duels."""
# TODO - ADD PHRASES
from telegram import Update, User, Message
from telegram.ext import CallbackContext
from main import randomizer
from main.helpers import validity_check, check_cooldown, record_user_chat_data
from main.database import *
from main.constants import DD


@validity_check
@check_cooldown
def duel(update: Update, context: CallbackContext) -> Message:
    """Duel the person if he has whitegloved you."""
    # Get users and record
    init_data = update.message.from_user
    targ_data = update.message.reply_to_message.from_user
    record_user_chat_data(update, context, init_data, targ_data)
    # Check if the target has whitegloved the initiator
    if not called_to_duel(update, init_data, targ_data):
        update.message.reply_text('Этот пользователь не вызывал вас на дуэль.')
        return
    # Proceed to the duel
    win_threshold = randomizer.uniform(0, DD['WIN_ROLL_CAP'])
    init_roll = get_win_chance(update, init_data)
    targ_roll = get_win_chance(update, targ_data)
    # Duel outcomes message
    outcome_storer = {
        'init': {
            'user': init_data,
            'score': tuple()
        },
        'targ': {
            'user': targ_data,
            'score': tuple()
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
    duel_result += (f'\nДуэль состоялась, [{targ_data.full_name}](tg://user?id={targ_data.id})'
                    ' забрал свою перчатку.')
    # Record outcome
    record_outcome(outcome_storer, update)
    # Result message
    update.message.reply_text(text=duel_result, parse_mode='Markdown')


@db_session
def called_to_duel(update: Update, init_data: User, targ_data: User) -> bool:
    """Check if the target has called the initiator onto a duel using /whiteglove."""
    if Scores[Users[targ_data.id], Chats[update.message.chat.id]].target_id \
            is Users[init_data.id]:
        return True
    return False


@db_session
def get_win_chance(update: Update, user_data: User) -> float:
    """Get the win chance of a user, accounting for the experience."""
    win_roll = randomizer.uniform(0, DD['RANDOM_ROLL_CAP'])
    user_score = Scores[Users[user_data.id], Chats[update.message.chat.id]]
    win_roll += (user_score.kills * DD['KILL_EXP'] +
                 user_score.deaths * DD['DEATH_EXP'] +
                 user_score.misses * DD['MISS_EXP'])
    return win_roll


@db_session
def record_outcome(outcome_storer: dict, update: Update) -> None:
    """Record the outcome in the database."""
    # Record both player data
    for player in outcome_storer.values():
        user_db_data = Scores[Users[player['user'].id],
                              Chats[update.message.chat.id]]
        # Add KDA
        user_db_data.kills += player['score'][0]
        user_db_data.deaths += player['score'][1]
        user_db_data.misses += player['score'][2]
    # Remove whiteglove from target, as the duel took place
    Scores[Users[outcome_storer['targ']['user'].id],
           Chats[update.message.chat.id]].target_id = None
    # Add cooldown
    Scores[Users[outcome_storer['init']['user'].id],
           Chats[update.message.chat.id]].last_duel = datetime.now()
