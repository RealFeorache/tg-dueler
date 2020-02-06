"""Module responsible for duels."""
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
    init_tag = f'[{init_data.first_name}](tg://user?id={init_data.id})'
    targ_data = update.message.reply_to_message.from_user
    targ_tag = f'[{targ_data.first_name}](tg://user?id={targ_data.id})'
    record_user_chat_data(update, context, init_data, targ_data)
    # Check if the target has whitegloved the initiator
    if not called_to_duel(update, init_data, targ_data):
        update.message.reply_text('Этот пользователь не вызывал вас на дуэль.')
        return
    # Proceed to the duel
    win_threshold = randomizer.uniform(0, DD['WIN_ROLL_CAP'])
    init_roll = get_win_chance(update)
    targ_roll = get_win_chance(update)
    # Duel outcomes message
    outcome_storer = {
        'init': {
            'user': init_data,
            'tag': init_tag,
            'score': tuple()
        },
        'targ': {
            'user': targ_data,
            'tag': targ_tag,
            'score': tuple()
        }
    }
    # Scenarios
    winner, loser = '', ''
    if init_roll < win_threshold and targ_roll < win_threshold:
        outcome_storer['init']['score'] = (0, 0, 1)
        outcome_storer['targ']['score'] = (0, 0, 1)
    elif init_roll > win_threshold and targ_roll > win_threshold:
        outcome_storer['init']['score'] = (1, 1, 0)
        outcome_storer['targ']['score'] = (1, 1, 0)
    elif init_roll > win_threshold:
        outcome_storer['init']['score'] = (1, 0, 0)
        outcome_storer['targ']['score'] = (0, 1, 0)
        winner, loser = init_tag, targ_tag
    elif targ_roll > win_threshold:
        outcome_storer['init']['score'] = (0, 1, 0)
        outcome_storer['targ']['score'] = (1, 0, 0)
        winner, loser = targ_tag, init_tag
    duel_result = generate_duel_results(update, outcome_storer, winner, loser)
    duel_result += (f'\nДуэль состоялась, [{targ_data.full_name}](tg://user?id={targ_data.id})'
                    ' забрал свою перчатку.')
    # Result message
    update.message.reply_text(text=duel_result, parse_mode='Markdown')


@db_session
def called_to_duel(update: Update, init_data: User, targ_data: User) -> bool:
    """Check if the target has called the initiator onto a duel using /whiteglove."""
    if Scores[Users[targ_data.id], Chats[update.message.chat.id]].target_id \
            is Users[init_data.id]:
        return True
    return False


def get_win_chance(update: Update) -> float:
    """Get the win chance of a user, accounting for the experience."""
    return randomizer.uniform(0, DD['RANDOM_ROLL_CAP']) + \
        get_user_exp(update)


@db_session
def get_user_exp(update: Update) -> float:
    """Get user EXP gained from duels."""
    user_score = Scores[Users[update.message.from_user.id],
                        Chats[update.message.chat.id]]
    exp = (user_score.kills * DD['KILL_EXP'] +
           user_score.deaths * DD['DEATH_EXP'] +
           user_score.misses * DD['MISS_EXP'])
    return exp


def generate_duel_results(update: Update, outcome: dict,
                          winner: str, loser: str) -> str:
    """Generate the duel results message."""
    from phrases.duel_phrases import (KILL_ACTIONS, DEATH_ACTIONS,
                                      MISS_ACTIONS, PHRASE_START,
                                      DRAW_ACTIONS, SUCC_ACTION,
                                      DRAW_PROBLEM)
    ch = randomizer.choice
    # Record into database
    record_outcome(update, outcome)
    # Start the phrase
    res = f'{ch(PHRASE_START)} '
    # Generate the middle
    for player in outcome.values():
        # Action of trying to kill
        res += f"{player['tag']} {ch(KILL_ACTIONS)}"
        # Miss or hit
        if player['score'] in [(0, 0, 1), (0, 1, 0)]:
            res += f', но {ch(MISS_ACTIONS)}. '
        else:
            res += ' и ' + ch(SUCC_ACTION) + '. '
    # Who won, who lost
    if winner:
        res += f'\n{loser} {ch(DEATH_ACTIONS)}! Победа за {winner}!'
    else:
        if randomizer.random() < 1/2:
            res += '\n' + ch(DRAW_PROBLEM)
        res += '\n' + ch(DRAW_ACTIONS)
    return res


@db_session
def record_outcome(update: Update, outcome: dict) -> None:
    """Record the outcome in the database."""
    # Record both player data
    for player in outcome.values():
        user_score = Scores[Users[player['user'].id],
                            Chats[update.message.chat.id]]
        # Add KDA
        user_score.kills += player['score'][0]
        user_score.deaths += player['score'][1]
        user_score.misses += player['score'][2]
    # Remove whiteglove from target, as the duel took place
    Scores[Users[outcome['targ']['user'].id],
           Chats[update.message.chat.id]].target_id = None
    # Add cooldown
    Scores[Users[outcome['init']['user'].id],
           Chats[update.message.chat.id]].last_duel = datetime.now()
