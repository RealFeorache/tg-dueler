"""List of constants."""
# Database constants
DATABASE_NAME = 'duels.sqlite'


# Duel constants, change only dictionary values
DUEL_COOLDOWN = 10  # 10 minutes
DD = {
    'RANDOM_ROLL_CAP': 0.75,
    'WINS_TO_MAX_EXP': 500,
    'WIN_ROLL_CAP': 0.45
}
DD['EXP_CAP'] = round(1 - DD['RANDOM_ROLL_CAP'], 2)
DD['KILL_EXP'] = (1 - DD['RANDOM_ROLL_CAP'])/DD['WINS_TO_MAX_EXP']
DD['DEATH_EXP'] = DD['KILL_EXP'] * -1/3
DD['MISS_EXP'] = DD['KILL_EXP'] * +1/3

# Dev user_id
DEV = 255295801
