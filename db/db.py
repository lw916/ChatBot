import configparser
import redis


# code for redis connection
def redis_connect():
    """
    This command is used to connect the redis database
    """
    config = configparser.ConfigParser()
    config.read(r"../conf/config.ini")  # read config file from config.ini
    return redis.Redis(host=(config['DATABASE']['HOST']), password=(config['DATABASE']['PASSWORD']),
                       port=(config['DATABASE']['PORT']))
