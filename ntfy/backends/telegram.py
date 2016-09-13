from os import path, makedirs

from appdirs import user_config_dir
from telegram_send import send, configure


CONFIG_DIR = user_config_dir('ntfy', 'dschep')
CONFIG_FILE = path.join(CONFIG_DIR, 'telegram.ini')


def notify(title, message, retcode=None):
    """Sends message over Telegram using telegram-send, title is ignored."""
    if not path.exists(CONFIG_FILE):
        if not path.exists(CONFIG_DIR):
            makedirs(CONFIG_DIR)
        print("Follow the instructions to configure the Telegram backend.\n")
        configure(CONFIG_FILE)
    send(messages=[message], conf=CONFIG_FILE)
