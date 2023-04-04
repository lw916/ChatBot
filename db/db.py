import configparser
import redis
import os


# code for redis connection
def redis_connect():
    """
    This command is used to connect the redis database
    """
    # config = configparser.ConfigParser()
    # config.read("../conf/config.ini")  # read config file from config.ini
    return redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']),
                       port=(os.environ['PORT']), decode_responses=True)


# storing userID with userName
def user_storing(redis_connection, userName, userID):
    """
    This is a function when user start to use the chatbot,
    bot would record the user's id and its name for other functions.
    """
    try:
        # for finding the user if the user in the database and avoid repeat record the userID
        if redis_connection.get(userName):
            return True
        else:
            redis_connection.set(userName, userID)
            return True

    except (IndexError, ValueError):
        return False


# database fuzzy query
def fuzzy_query(redis_connection, query):
    """
    This is the function is for fuzzy query the database.
    """
    try:
        keys = redis_connection.scan(match=query + "*")
        return keys
    except (IndexError, ValueError):
        return []


# get user id by username
def get_userid(redis_connection, userName):
    """
    This is the function for return the userID with username.
    UserName have record, return the userID.
    UserName don't have record or fail to get, return None.
    """
    try:
        userID = redis_connection.get(userName)
        if userID:
            return userID
        else:
            return None
    except (IndexError, ValueError):
        return None
