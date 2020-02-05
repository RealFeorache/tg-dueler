"""Database related module."""
from pony.orm import *
from main import constants
from datetime import datetime


db = Database()


class Users(db.Entity):
    """Telegram users."""

    id = PrimaryKey(int)
    # The user’s first_name, followed by (if available) last_name
    full_name = Required(str)
    username = Optional(str)
    # If username is available, returns a t.me link of the user.
    link = Optional(str)
    scores = Set('Scores', reverse='user_id')
    tscores = Set('Scores', reverse='target_id')


class Chats(db.Entity):
    """Telegram chats."""

    id = PrimaryKey(int)
    title = Optional(str)
    # If the chat has a username, returns a t.me link of the chat.
    link = Optional(str)
    scores = Set('Scores')
    duel_cooldown = Optional(int, default=10)


class Scores(db.Entity):
    """Duel scores."""

    user_id = Required(Users, reverse='scores')
    chat_id = Required(Chats)
    target_id = Optional(Users, reverse='tscores')
    last_duel = Optional(datetime)
    wins = Optional(int, default=0)
    losses = Optional(int, default=0)
    misses = Optional(int, default=0)
    PrimaryKey(user_id, chat_id)


db.bind(provider='sqlite', filename=constants.DATABASE_NAME, create_db=True)

db.generate_mapping(create_tables=True)
