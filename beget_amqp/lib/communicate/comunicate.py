# -*- coding: utf-8 -*-
import redis
from ..helpers.logger import Logger


class Communicate(object):
    PREFIX_QUESTION = 'q_'
    PREFIX_ANSWER = 'a_'

    LOCAL_STORAGE_LIVE_TIME = 60 * 60

    KEY_SERVICE_LIST = 'amqp_services'

    def __init__(self, socket="/var/run/redis/redis.sock"):
        self.logger = Logger.get_logger()
        self.redis = redis.StrictRedis(unix_socket_path=socket)
