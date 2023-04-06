from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import os
from db.db import redis_connect, user_storing, fuzzy_query, get_userid
import requests
import logging

global redis_connection

SEARCH = range(2)
RECIPIENT, MESSAGE = range(2)
ENTER_MOVIE_NAME = 0


# main function part
# main function of starting telegram bot
def bot():
    """
    This is the main function for this backend telegram bot.
    """

    # read the config file
    # global config_content
    # config_content = configparser.ConfigParser()  # import ConfigParser to read the config file
    # config_content.read(r"../conf/config.ini")  # read config file from config.ini

    # connect redis database
    global redis_connection
    redis_connection = redis_connect()

    # set the telegram bot token
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    # setup for logging on the terminal
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # add different command into the telegram bot
    dispatcher.add_handler(CommandHandler("start", start))  # inject start command
    dispatcher.add_handler(CallbackQueryHandler(start_menu_actions))  # inject start menu function handler
    dispatcher.add_handler(search_conversation_handler)  # inject search conversation handler
    updater.dispatcher.add_handler(conv_handler)  # inject conversation handler for push
    updater.dispatcher.add_handler(review_conv_handler)  # inject conversation handler for movieReview()
    dispatcher.add_handler(CommandHandler("help", help_command))  # inject help command
    dispatcher.add_handler(CommandHandler("hello", hello))  # inject greet command
    dispatcher.add_handler(CommandHandler("push", push))  # inject push message to others command
    dispatcher.add_handler(CommandHandler("down1", down1))  # inject down command from mood selection
    dispatcher.add_handler(CommandHandler("calm2", calm2))  # inject calm command from mood selection
    dispatcher.add_handler(CommandHandler("happy3", happy3))  # inject happy command from mood selection
    dispatcher.add_handler(CommandHandler("exciting4", exciting4))  # inject exciting command from mood selection
    dispatcher.add_handler(CommandHandler("romance5", romance5))  # inject romance command from mood selection
    dispatcher.add_handler(CommandHandler("yes1", yes1))  # inject yes command for movie recommendation on down function
    dispatcher.add_handler(CommandHandler("no", no))  # inject no command for movie recommendation from down function
    dispatcher.add_handler(CommandHandler("yes2", yes2))  # inject yes command for movie recommendation on calm function
    dispatcher.add_handler(CommandHandler("yesReview", yesReview))  # inject yes command for movie reviews
    dispatcher.add_handler(
        CommandHandler("enterMovieName", enterMovieName))  # command under movieReview conversation handler
    dispatcher.add_handler(CommandHandler("recipient", recipient))  # command under push conversation handler
    dispatcher.add_handler(CommandHandler("message", message))  # command under push conversation handler
    dispatcher.add_handler(CommandHandler("send", send))  # command under push conversation handler

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
        keyboard = [[InlineKeyboardButton('Chat with bot', callback_data='hello')]]
        start_menu_keyboard = InlineKeyboardMarkup(keyboard)
        # get people user from update
        userName = update.effective_chat["last_name"] + update.effective_chat["first_name"]
        user_storing(redis_connection, userName, update.effective_chat["id"])
        # inject main menu to start command
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
    elif query.data == 'down1':
        down1(update, context)
    elif query.data == 'calm2':
        calm2(update, context)
    elif query.data == 'happy3':
        happy3(update, context)
    elif query.data == 'exciting4':
        exciting4(update, context)
    elif query.data == 'romance5':
        romance5(update, context)
    elif query.data == 'yes1':
        yes1(update, context)
    elif query.data == 'no':
        no(update, context)
    elif query.data == 'yes2':
        yes2(update, context)
    elif query.data == 'yesReview':
        yesReview(update, context)
    elif query.data == 'sendmessage':
        sendmessage(update, context)
    elif query.data == 'recipient':
        recipient(update, context)
    elif query.data == 'message':
        message(update, context)
    elif query.data == 'send':
        send(update, context)
    elif query.data == 'enterMovieName':
        enterMovieName(update, context)
    else:
        update.message.reply_text('Please select the right command!')


# start command part end.


# greeting command part start
# Greeting user
def hello(update, context):
    """
    This code is used to greeting user.
    When user use /hello would return user's message:
    Good day, user and provide mood selection.
    """
    try:
        # keyboard to provide mood selection
        Mkeyboard = [[InlineKeyboardButton('⭐️', callback_data='down1')],
                     [InlineKeyboardButton('⭐️⭐️', callback_data='calm2')],
                     [InlineKeyboardButton('⭐️⭐️⭐️', callback_data='happy3')],
                     [InlineKeyboardButton('⭐️⭐️⭐️⭐️', callback_data='exciting4')],
                     [InlineKeyboardButton('⭐️⭐️⭐️⭐️⭐️', callback_data='romance5')]]
        mood_menu_keyboard = InlineKeyboardMarkup(Mkeyboard)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 reply_markup=mood_menu_keyboard,
                                 text="Good day, How are you feeling today " + update.effective_chat[
                                     "last_name"] + ' ' +
                                      update.effective_chat["first_name"] + "? Please rate your feeling below")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /down1, /calm2, '
                                      '/happy3, /exciting4 or /romance5')

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

# test database part
# @TODO This part must be removed in the future
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
                                      redis_connection.get(msg) + ' times.')
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
# push data to others part end

# mood functions

def down1(update, context):
    """
    This code is used to play the function when user is feeling down
    """
    mood = "sad"
    url = "http://127.0.0.1/emotion?mood=" + mood
    response = requestBackend(url)

    print(response)

    try:
        # keyboard to ask if user want movie recommendation
        downkeyboard = [[InlineKeyboardButton('Yes', callback_data='yes1')],
                        [InlineKeyboardButton('No', callback_data='no')]]
        down_menu_keyboard = InlineKeyboardMarkup(downkeyboard)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 reply_markup=down_menu_keyboard,
                                 text="Hi " + update.effective_chat["last_name"] + ',\n' + update.effective_chat[
                                     "first_name"] +
                                      response + "\n" + "\n Would you also like some movie recommendations from us to cheer up?")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /down1')


def calm2(update, context):
    """
    This code is used to play the function when user is feeling calm
    """
    mood = "calm"
    url = "http://127.0.0.1/emotion?mood=" + mood
    response = requestBackend(url)

    print(response)

    try:
        # keyboard to ask if user want movie recommendation
        calmkeyboard = [[InlineKeyboardButton('Yes', callback_data='yes2')],
                        [InlineKeyboardButton('No', callback_data='no')]]
        calm_menu_keyboard = InlineKeyboardMarkup(calmkeyboard)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 reply_markup=calm_menu_keyboard,
                                 text="Hi " + update.effective_chat["last_name"] + ' ' + update.effective_chat[
                                     "first_name"] +
                                      response + "\n" + "\n Would you also like some movie recommendations from us to cheer up?")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /calm2')


def happy3(update, context):
    """
    This code is used to play the function when user is feeling happy
    """
    mood = "happy"
    url = "http://127.0.0.1/recommend?mood=" + mood
    response = requestBackend(url)

    print(response)

    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="These are the movie recommendations based on your current mood" + response
                                      + "\n" * 2 + "Would you also like to see reviews?\n" + "\n" +
                                      "Select /yesReview if you want to read review or /no to quit")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /happy3')


def exciting4(update, context):
    """
    This code is used to play the function when user is feeling exciting
    """
    mood = "exciting"
    url = "http://127.0.0.1/recommend?mood=" + mood
    response = requestBackend(url)

    print(response)

    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="These are the movie recommendations based on your current mood" + response
                                      + "\n" * 2 + "Would you also like to see reviews?\n" + "\n" +
                                      "Select /yesReview if you want to read review or /no to quit")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /exciting4')


def romance5(update, context):
    """
    This code is used to play the function when user is feeling romance
    """
    mood = "romance"
    url = "http://127.0.0.1/recommend?mood=" + mood
    response = requestBackend(url)

    print(response)

    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="These are the movie recommendations based on your current mood" + response
                                      + "\n" * 2 + "Would you also like to see reviews?\n" + "\n" +
                                      "Select /yesReview if you want to read review or /no to quit")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /romance5')


def yes1(update, context):
    """
    This code is used to play the function when user is feeling down (1 star mood) and want movie recommendations
    """
    mood = "down"
    url = "http://127.0.0.1/recommend?mood=" + mood
    response = requestBackend(url)

    print(response)

    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="These are the movie recommendations based on your current mood" + response
                                      + "\n" * 2 + "Would you also like to see reviews?\n" + "\n" +
                                      "Select /yesReview if you want to read review or /no to quit")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /yes')


def no(update, context):
    """
    This code is used to play the function when user is feeling down and do not want movie recommendations
    """
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Thank you for using our chatbot, see you!")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /no')


def yes2(update, context):
    """
    This code is used to play the function when user rate his mood 2 stars
    """
    mood = "sad"
    url = "http://127.0.0.1/recommend?mood=" + mood
    response = requestBackend(url)

    print(response)
    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="These are the movie recommendations based on your current mood" + response
                                      + "\n" * 2 + "Would you also like to see reviews?\n" + "\n" +
                                      "Select /yesReview if you want to read review or /no to quit")

    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /yes2')


def yesReview(update, context):
    """
    This code is used for movie review generations where user is required to input movie name
    """
    # Prompt user to enter a movie name
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Enter a movie name for reviews to be generated:")

    return ENTER_MOVIE_NAME


def enterMovieName(update, context):
    movie = update.message.text

    # Send GET request to Flask app to get movie review
    url = "http://127.0.0.1/review?movie=" + movie
    response = requestBackend(url)
    print(response)

    try:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=response + "\n" + "\n Would you also like to send a message to other user "
                                                        "regarding the review? \n" + "\n "
                                      + "Select /push to send a message to your friend or /no to quit")
        return ConversationHandler.END
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /yesReview')


def review_cancel(update, context):
    update.message.reply_text('Search Conversation cancelled.')
    return ConversationHandler.END


review_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('yesReview', yesReview)],
    states={
        ENTER_MOVIE_NAME: [MessageHandler(Filters.text & ~Filters.command, enterMovieName)]
    },
    fallbacks=[CommandHandler('review_cancel', review_cancel)],
)


# backup - to be removed
def sendmessage(update, context):
    """
    This code is used to ask if user would like to send message to other user
    """
    try:
        # keyboard to provide Review
        messagekeyboard = [[InlineKeyboardButton('Yes', callback_data='push')],
                           [InlineKeyboardButton('No', callback_data='no1')]]
        message_keyboard = InlineKeyboardMarkup(messagekeyboard)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 reply_markup=message_keyboard,
                                 text="Would you like to send a message to other user?")
    except (IndexError, ValueError):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Oh right, your command might be wrong. This command usage is: /sendmessage')


def send(user_ID, message):
    """
    This is a function for bot to transfer message to other user who also subscribe the bot.
    """

    try:
        requests.get("https://api.telegram.org/bot"
                     + str(os.environ['ACCESS_TOKEN'])
                     + "/sendMessage?chat_id="
                     + str(user_ID)
                     + "&text="
                     + str(message)
                     )
        return True
    except (IndexError, ValueError):
        return False


def push(update, context):
    """
    This is a command for testing the function of pushing the message to other user
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please enter the username of the recipient:")
    return RECIPIENT


def recipient(update, context):
    # Check if the recipient username is valid
    recipient_username = update.message.text
    keys = fuzzy_query(redis_connection, recipient_username)
    print(keys)
    if not keys[1]:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Username invalid or not subscribed to the bot.")
        return ConversationHandler.END
    else:
        if recipient_username not in keys[1]:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Username not found in the database. Please try again.")
            return RECIPIENT
        user_id = get_userid(redis_connection, recipient_username)
        if user_id:
            context.user_data['recipient_user_id'] = user_id
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please enter the message to send to " + recipient_username + "")
        return MESSAGE


def message(update, context):
    message_to_forward = update.message.text
    user_id = context.user_data.get('recipient_user_id', None)
    if user_id:
        send(user_id, message_to_forward)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Message forwarded to " + user_id + ".")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Message is failed to sent. Please try again")
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled.")
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('push', push)],
    states={
        RECIPIENT: [MessageHandler(Filters.text & ~Filters.command, recipient)],
        MESSAGE: [MessageHandler(Filters.text & ~Filters.command, message)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


def requestBackend(url: str) -> str:
    """
    url: you need to concat the params to a url before using this function
    For example: mood=sad
        url = '127.0.0.1:4000/emotion?mood=' + mood
        OR
        url = '127.0.0.1:4000/recommend?mood=' + mood
    You should adjust the prefix url with your need.
    """
    payload = {}
    headers = {}
    response = requests.request('GET', url, headers=headers, data=payload)

    # response.encoding='utf-8'
    # if text cannot show normally, use it
    return response.text
