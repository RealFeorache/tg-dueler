"""Telegram bot with the sole function of duels."""

from main import updater, dispatcher
from main.whiteglove import whiteglove
from main.duel import duel
from main.admicommands import set_duel_cooldown
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

__author__ = "Vlad Chitic"
__copyright__ = "Copyright 2020, Vlad Chitic"
__credits__ = ["Vlad Chitic"]
__license__ = "MIT License"
__version__ = "0.1 prototype"
__maintainer__ = "Vlad Chitic"
__email__ = "feorache@protonmail.com"
__status__ = "Prototype"


def bothelp(update: Update, context: CallbackContext):
    """Send the help message."""
    help_text = (
        "/whiteglove - вызвать на дуэль\n"
        "/duel - провести дуэль с вызвавшим\n"
        "/setduelcooldown [число] - изменить задержку на дуэль (для админов)\n"
        "Автор: @doitforricardo"
    )
    update.message.reply_text(help_text)
    pass


def main():
    dispatcher.add_handler(CommandHandler("whiteglove", whiteglove))
    dispatcher.add_handler(CommandHandler("duel", duel))
    dispatcher.add_handler(CommandHandler(
        "setduelcooldown", set_duel_cooldown))
    dispatcher.add_handler(CommandHandler("help", bothelp))
    updater.start_polling(clean=True)
    updater.idle()


main()
