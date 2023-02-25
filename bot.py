import logging
import os
import random
import sys
import re
import random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(webhook_url(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def webhook_url(app_name, token):
    return "https://{}.herokuapp.com/{}".format(app_name, token)


def start_handler(bot, update):
    update.message.reply_text("Hi, I'm dadbot!")


def match_boundary(needle, haystack):
    exp = "^(({0})|(.*[\s\n,.!;]+{0}))(\W|$)".format(needle)
    return re.search(exp, haystack)


def dad_joke_trigger_loc(usr_msg):
    joke_triggers = [
        "i am",
        "im",
        "i'm",
        "i`m"
    ]

    locs = [match_boundary(x, usr_msg).end() for x in joke_triggers
        if match_boundary(x, usr_msg) is not None]
    return min(locs, default=-1)


def dad_joke_resp_name(usr_msg, loc):
    return usr_msg[loc:] \
        .replace(';',',') \
        .replace('.',',') \
        .replace('!',',') \
        .replace('?',',') \
        .replace('\n', ',') \
        .split(',')[0].strip()


def build_joke(joke_name):
    return "Hi " + joke_name + ", I'm dad."


def random_where_dad_reply():
    opts = [
        "It's always \"where's dad\" but never \"how's dad\".",
        "Right here.",
        "...",
        "Hello!",
        "Buying milk."
    ]

    return random.choice(opts)


def where_dad_trigger_loc(usr_msg):
    joke_triggers = [
        "wheres dad",
        "where's dad",
        "where`s dad",
        "where is dad",
        "wheres @daddddddbot",
        "where's @daddddddbot",
        "where`s @daddddddbot",
        "where is @daddddddbot",
        "wheres dadbot",
        "where's dadbot",
        "where`s dadbot",
        "where is dadbot"
    ]

    locs = [match_boundary(x, usr_msg).end() for x in joke_triggers
        if match_boundary(x, usr_msg) is not None]
    return min(locs, default=-1)


def where_user_trigger_loc(usr_msg):
    joke_triggers = [
        "wheres(?= )",
        "where's(?= )",
        "where`s(?= )",
        "where is(?= )",
    ]

    locs = [match_boundary(x, usr_msg).end() for x in joke_triggers
        if match_boundary(x, usr_msg) is not None]

    target = min(locs, default=-1)

    if target != -1:
        usr_msg = usr_msg[target:] \
            .replace(';',',') \
            .replace('.',',') \
            .replace('!',',') \
            .replace('?',',') \
            .replace('\n', ',') \
            .split(',')[0].strip()
        if len(usr_msg) > 0:
            return target
    else:
        return -1

    return -1


def be_dadbot(bot, update):
    usr_msg = update.message.text
    loc = dad_joke_trigger_loc(usr_msg.lower())

    if loc != -1:
        resp_name = dad_joke_resp_name(usr_msg, loc)
        if len(resp_name) > 0:
            resp = build_joke(resp_name)
            update.message.reply_text(resp)
            return

    loc = where_dad_trigger_loc(usr_msg.lower())

    if loc != -1:
        update.message.reply_text(random_where_dad_reply())
        return

    loc = where_user_trigger_loc(usr_msg.lower())

    if loc != -1:
        update.message.reply_text("Buying cigarettes.")
        return

if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, be_dadbot))

    run(updater)
