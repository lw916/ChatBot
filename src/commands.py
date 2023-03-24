from telegram.ext import Updater, CommandHandler
import configparser
from db.db import redis_connect
import requests
import logging
import redis

global redis_connection
global config_content


# main function of starting telegram bot
def bot():
    """
    This is the main function for this backend telegram bot.
    """

    # read the config file
    global config_content
    config_content = configparser.ConfigParser()
    config_content.read(r"../conf/config.ini")  # read config file from config.ini

    # connect redis database
    global redis_connection
    redis_connection = redis_connect()

    # set the telegram bot token
    updater = Updater(token=(config_content['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # add different command into the telegram bot
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("push", push))
    dispatcher.add_handler(CommandHandler("add", add))

    # Start the telegram bot
    updater.start_polling()
    updater.idle()


# push message to other user
# example: https://api.telegram.org/bot6[botID]/sendMessage?chat_id=[userID]&text=[text message]
def send(user_ID, message):
    """
    This is a function for bot to transfer message to other user who also subscribe the bot.
    """

    try:
        requests.get("https://api.telegram.org/bot"
                     + str(config_content['TELEGRAM']['ACCESS_TOKEN'])
                     + "/sendMessage?chat_id="
                     + str(user_ID)
                     + "&text="
                     + str(message)
                     )
        return True
    except (IndexError, ValueError):
        return False


# test message pushing
def push(update, context):
    """
    This is a command for testing the function of pushing the message to other user
    """
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I have receive your require and try to push message to your friends!")
        if send(update.effective_chat["id"], "This is a testing message for "
                                             + update.effective_chat["last_name"]
                                             + ' '
                                             + update.effective_chat["first_name"]
                                             + "!"):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Your message might successfully push to your friend.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Your message might fail to push to your friend.")
    except (IndexError, ValueError):
        update.message.reply_text('So sorry, I have a mistake of pushing message to your friends.')


# start the bot
def start(update, context):
    """
    This function is used to start the bot chat.
    This is the first time user subscribe the bot and the bot's reply!
    """
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Hi! " + update.effective_chat["last_name"] + ' ' + update.effective_chat[
                                     "first_name"] + ',\n'
                                      + 'I am telegram bot provide movie recommending and sharing for you.\n'
                                      + 'Hope you could get your best result here!\n'
                                      + 'Please use the bot command to chat with me!'
                                 )
    except (IndexError, ValueError):
        update.message.reply_text('Oh right, your command might be wrong. This command usage is: /start')


# Greeting user
def hello(update, context):
    """
    This code is used to greeting user.
    When user use /hello would return user's message:
    Good day, user.
    """
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Good day, " + update.effective_chat["last_name"] + ' ' +
                                      update.effective_chat["first_name"])
    except (IndexError, ValueError):
        update.message.reply_text('Oh right, your command might be wrong. This command usage is: /hello')


# Help command
def help_command(update, context):
    """
    This command is provided user with this bot help.
    Like provide some command example for user.
    """
    try:
        update.message.reply_text('Hello! ' + update.effective_chat["last_name"] + ' ' +
                                  update.effective_chat["first_name"] + '. This is a helping message.')
    except (IndexError, ValueError):
        update.message.reply_text('Oh right, your command might be wrong. This command usage is: /help')


# Database calculate
def add(update, context):
    """
    THis command is provided to test redis services
    """
    try:
        msg = context.args[0]
        redis_connection.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +
                                  redis_connection.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Oh right, your command might be wrong. This command usage: /add <keyword>')
