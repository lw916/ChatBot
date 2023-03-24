import configparser
import redis


# code for redis connection
def redis_connect():
    config = configparser.ConfigParser()
    config.read(r"../conf/config.ini")
    return redis.Redis(host=(config['DATABASE']['HOST']), password=(config['DATABASE']['PASSWORD']), port=(config['DATABASE']['PORT']))
