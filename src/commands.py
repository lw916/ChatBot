from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import configparser
from db.db import redis_connect, user_storing, fuzzy_query
import requests
import logging

global redis_connection
global config_content

SEARCH = range(2)


# main function part
# main function of starting telegram bot
def bot():
    """
    This is the main function for this backend telegram bot.
    """

    # read the config file
    global config_content
    config_content = configparser.ConfigParser()  # import ConfigParser to read the config file
    config_content.read(r"../conf/config.ini")  # read config file from config.ini

    # connect redis database
    global redis_connection
    redis_connection = redis_connect()

    # set the telegram bot token
    updater = Updater(token=(config_content['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    # setup for logging on the terminal
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # add different command into the telegram bot
    dispatcher.add_handler(CommandHandler("start", start))  # inject start command
    dispatcher.add_handler(CallbackQueryHandler(start_menu_actions))  # inject start menu function handler
    dispatcher.add_handler(search_conversation_handler)  # inject search conversation handler
    dispatcher.add_handler(CommandHandler("help", help_command))  # inject help command
    dispatcher.add_handler(CommandHandler("hello", hello))  # inject greet command
    dispatcher.add_handler(CommandHandler("push", push))  # inject push message to others command
    # @TODO database function will be remove in the future
    dispatcher.add_handler(CommandHandler("add", add))  # inject database testing command
    dispatcher.add_handler(CommandHandler("search", search_user))  # inject search user command

    # Start the telegram bot
    updater.start_polling()
    updater.idle()
# main function part end


# start command
# start the bot
def start(update, context):
    """
    This function is used to start the bot chat.
    This is the first time user subscribe the bot and the bot's reply!
    """
    try:
        # Main menu edit/design
        keyboard = [[InlineKeyboardButton('Chat with bot', callback_data='hello')],
                    [InlineKeyboardButton('Bot help', callback_data='help')],
                    [InlineKeyboardButton('Push message', callback_data='push')]]
        start_menu_keyboard = InlineKeyboardMarkup(keyboard)
        userName = update.effective_chat["last_name"] + update.effective_chat["first_name"]
        user_storing(redis_connection, userName, update.effective_chat["id"])
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 reply_markup=start_menu_keyboard,
                                 text="Hi! " + userName
                                      + ',\n'
                                      + 'I am telegram bot provide movie recommending and sharing for you.\n'
                                      + 'Hope you could get your best result here!\n'
                                      + 'Please use the bot command to chat with me!',

                                 )
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /start')


# main menu callback reply
def start_menu_actions(update, context):
    query = update.callback_query
    if query.data == 'hello':
        hello(update, context)
    elif query.data == 'help':
        help_command(update, context)
    elif query.data == 'push':
        push(update, context)
    else:
        update.message.reply_text('Please select the right command!')


# start command part end.


# greeting command part start
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
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /hello')


# greet part end


# Help command
def help_command(update, context):
    """
    This command is provided user with this bot help.
    Like provide some command example for user.
    """
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Hello! ' + update.effective_chat["last_name"] + ' ' +
                                      update.effective_chat["first_name"] + '. This is a helping message.')
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /help')


# Help part end


# Database calculate
def add(update, context):
    """
    THis command is provided to test redis services
    """
    try:
        msg = context.args[0]
        redis_connection.incr(msg)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You have said ' + msg + ' for ' +
                                      redis_connection.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage: /add <keyword>')


# Database part end


# This part is for user searching question
# For searching user's question
def search_user_question(update, context):
    """
    When press the start button and use the search button
    bot would ask the user for its name
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Please enter the username for searching the user.')
    return SEARCH


# search for the user
def search_user(update, context):
    """
    This function is the command for searching the user.
    """
    try:
        match_word_from_question = update.message.text
        keys = fuzzy_query(redis_connection, match_word_from_question)
        if not keys[1]:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Can not find the user, please check your match key")
            return ConversationHandler.END
        else:
            friend_list = ""
            for i in keys[1]:
                friend_list += i + "\n"
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Friend List:\n" + friend_list + "Please check the list if someone is your "
                                                                           "friends.")
            return ConversationHandler.END
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Sorry, your command might be wrong.Usage: /search <keyword>. Please try again.')
        return ConversationHandler.END


def search_cancel(update, context):
    update.message.reply_text('Search Conversation cancelled.')
    return ConversationHandler.END


search_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('search', search_user_question)],
    states={
        SEARCH: [MessageHandler(Filters.text & ~Filters.command, search_user)],
    },
    fallbacks=[CommandHandler('cancel', search_cancel)],
)


# search part end


# push message to other user part
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
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='So sorry, I have a mistake of pushing message to your friends.')
# push data to others part end
