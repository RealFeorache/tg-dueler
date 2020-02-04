"""Module dedicated to bot initiation variables that are usable in other modules."""
import logging
import random
import main.helpers

from telegram.ext import Updater

# Setup logging
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

# Create a randomizer
randomizer = random.SystemRandom()

# Setup python-telegram-bot
updater = Updater(
    token="1081584312:AAEQjUi4sRx-vI2LxE4TgXCzrxmADBCeohY",
    use_context=True
)
dispatcher = updater.dispatcher
