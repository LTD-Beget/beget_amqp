# -*- coding: utf-8 -*-
import redis
from ...helpers.logger import Logger


class StorageRedis(object):
    CONSUMER_PREFIX = 'consumer'

    def __init__(self, socket="/var/run/redis/redis.sock"):
        self.redis = redis.StrictRedis(unix_socket_path=socket)
        self.logger = Logger.get_logger()
