"""List of constants."""
# Database constants
DATABASE_NAME = 'duels.sqlite'


# Duel constants, change only dictionary values
DD = {
    'RANDOM_ROLL_CAP': 0.8,
    'WINS_TO_MAX_EXP': 900,
    'WIN_ROLL_CAP': 0.5
}
DD['EXP_CAP'] = 1 - DD['RANDOM_ROLL_CAP']
DD['KILL_EXP'] = (1 - DD['RANDOM_ROLL_CAP'])/DD['WINS_TO_MAX_EXP']
DD['DEATH_EXP'] = DD['KILL_EXP'] * -1/2
DD['MISS_EXP'] = DD['KILL_EXP'] * +1/3

# Dev user_id
DEV = 255295801
