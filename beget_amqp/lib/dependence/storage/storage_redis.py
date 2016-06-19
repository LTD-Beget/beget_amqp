# -*- coding: utf-8 -*-
import redis
from ...helpers.logger import Logger


class StorageRedis(object):
    DEPENDENCE_PREFIX = 'dependence'

    def __init__(self, redis_socket="/var/run/redis/redis.sock"):
        self.redis = redis.StrictRedis(unix_socket_path=redis_socket)
        self.logger = Logger.get_logger()
