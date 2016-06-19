# -*- coding: utf-8 -*-
import time
import sys
from .storage_redis import StorageRedis


class MessageStorageRedis(StorageRedis):
    """
    Локальное хранение сообщений и информации о нем.
    """

    SIZE_MEGABYTE = 1048576

    def __init__(self, worker_id, amqp_vhost, amqp_queue, redis_socket="/var/run/redis/redis.sock"):
        super(MessageStorageRedis, self).__init__(redis_socket)
        self.worker_id = worker_id
        self.amqp_vhost = amqp_vhost
        self.amqp_queue = amqp_queue

    def message_save(self, message_amqp, body, properties):
        """
        :param body:
        :param message_amqp:
        :param properties
        :type message_amqp: MessageToPackage

        :return:
        """

        if not message_amqp.id:
            return
        key = self.get_message_key(message_amqp)
        self.debug('save message: %s, key: %s', message_amqp.id, key)

        self.redis.hset(key, self.KEY_DONE, self.MESSAGE_DONE_NOT)
        self.redis.hset(key, self.KEY_WORKER, self.worker_id)
        self.redis.hset(key, self.KEY_HEADER, properties)

        if self.SIZE_MEGABYTE < sys.getsizeof(body):
            self.redis.hset(key, self.KEY_BODY, 'Warning: body to long for logging')
        else:
            self.redis.hset(key, self.KEY_BODY, body)

        self.redis.hset(key, self.KEY_TIME_START_WAIT, time.time())
        self.redis.expire(key, self.LOCAL_STORAGE_LIVE_TIME)

    def message_save_start_time(self, message_amqp):
        key = self.get_message_key(message_amqp)
        self.redis.hset(key, self.KEY_TIME_START_WORK, time.time())

    def message_set_done(self, message_amqp):
        if not message_amqp.id:
            return
        self.debug('set done message: %s', message_amqp.id)
        key = self.get_message_key(message_amqp)
        self.redis.hset(key, self.KEY_DONE, self.MESSAGE_DONE_YES)
        self.redis.hset(key, self.KEY_TIME_END_WORK, time.time())
        self.redis.hdel(key, self.KEY_WORKER)
        self.redis.expire(key, self.LOCAL_STORAGE_LIVE_TIME)

    def is_duplicate_message(self, message_amqp):
        key = self.get_message_key(message_amqp)
        message_status = self.redis.hget(key, self.KEY_DONE)
        result = message_status is not None
        self.debug('is duplicate message: %s', result)
        return result

    def is_done_message(self, message_amqp):
        key = self.get_message_key(message_amqp)
        message_status = self.redis.hget(key, self.KEY_DONE)
        result = message_status == self.MESSAGE_DONE_YES
        self.debug('is done message: %s', result)
        return result

    def get_worker_id_by_message(self, message_amqp):
        if not message_amqp.id:
            return None
        key = self.get_message_key(message_amqp)
        worker_id = self.redis.hget(key, self.KEY_WORKER)
        return worker_id

    def get_message_key(self, message_amqp=None):
        key = '{}:{}:{}'.format(self.MESSAGE_PREFIX, self.amqp_vhost, self.amqp_queue)

        if message_amqp is not None:
            key += ':{}'.format(message_amqp.id)

        return key

    def debug(self, msg, *args):
        self.logger.debug('RedisMessageStore: ' + msg, *args)
