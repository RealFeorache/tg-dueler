"""Telegram bot with the sole function of duels."""

from main import updater, dispatcher
from main.whiteglove import whiteglove
# from main.duel import duel
from telegram.ext import CommandHandler

__author__ = "Vlad Chitic"
__copyright__ = "Copyright 2020, Vlad Chitic"
__credits__ = ["Vlad Chitic"]
__license__ = "MIT License"
__version__ = "0.1 prototype"
__maintainer__ = "Vlad Chitic"
__email__ = "feorache@protonmail.com"
__status__ = "Prototype"


def main():
    dispatcher.add_handler(CommandHandler("whiteglove", whiteglove))
    # dispatcher.add_handler(CommandHandler("duel", duel))
    updater.start_polling(clean=True)
    updater.idle()


main()
