# -*- coding: utf-8 -*-
import redis
from ...helpers.logger import Logger


class StorageRedis(object):
    KEY_DONE = 'done'
    KEY_WORKER = 'worker_id'
    KEY_HEADER = 'headers'
    KEY_BODY = 'body'
    KEY_TIME_START_WAIT = 'start_wait'
    KEY_TIME_START_WORK = 'start_work'
    KEY_TIME_END_WORK = 'end_work'

    MESSAGE_DONE_NOT = '0'  # Сообщение было отработано
    MESSAGE_DONE_YES = '1'  # Сообщение еще не отработано

    MESSAGE_PREFIX = 'msg_store'

    LOCAL_STORAGE_LIVE_TIME = 60 * 60 * 24 * 7  # Время хранения информации в локальном хранилище

    def __init__(self, socket="/var/run/redis/redis.sock"):
        self.redis = redis.StrictRedis(unix_socket_path=socket)
        self.logger = Logger.get_logger()
