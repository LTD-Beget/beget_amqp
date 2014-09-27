# -*- coding: utf-8 -*-
import redis
from .helpers.logger import Logger


class MessageStorageRedis(object):
    """
    Класс решает следующие задачи:
      - Локальное хранение сообщений и их статуса работы на случай проблем с коннектом к AMQP

    Принцип работы:
      - Ключ: уникальный id сообщения
      - По ключу имеем 2 хеша(ключа):
        - done: задача выполнена или нет
        - worker_id: уникальный id воркера который занима(лся|ется) задачей

      - Если сообщения нет в redis: считаем, что сообщение небыло создано
    """

    KEY_DONE = 'done'
    KEY_WORKER = 'worker_id'

    MESSAGE_DONE_NOT = '0'  # Сообщение было отработано
    MESSAGE_DONE_YES = '1'  # Сообщение еще не отработано

    LOCAL_STORAGE_LIVE_TIME = 60 * 60 * 24 * 2  # Время хранения информации в локальном хранилище

    def __init__(self, worker_id, socket="/var/run/redis/redis.sock", service_name='amqp_message'):
        self.worker_id = worker_id
        self.service_name = service_name + ':'
        self.redis = redis.StrictRedis(unix_socket_path=socket)
        self.logger = Logger.get_logger()

    def message_save(self, message_amqp):
        if not message_amqp.id:
            return
        self.debug('save message: %s', message_amqp.id)
        key = self.get_key(message_amqp)
        self.redis.hset(key, self.KEY_DONE, self.MESSAGE_DONE_NOT)
        self.redis.hset(key, self.KEY_WORKER, self.worker_id)
        self.redis.expire(key, self.LOCAL_STORAGE_LIVE_TIME)

    def message_set_done(self, message_amqp):
        if not message_amqp.id:
            return
        self.debug('set done message: %s', message_amqp.id)
        key = self.get_key(message_amqp)
        self.redis.hset(key, self.KEY_DONE, self.MESSAGE_DONE_YES)
        self.redis.hdel(key, self.KEY_WORKER)
        self.redis.expire(key, self.LOCAL_STORAGE_LIVE_TIME)

    def is_duplicate_message(self, message_amqp):
        message_status = self.redis.hget(self.service_name + message_amqp.id, self.KEY_DONE)
        result = message_status is not None
        self.debug('is duplicate message: %s', result)
        return result

    def is_done_message(self, message_amqp):
        message_status = self.redis.hget(self.service_name + message_amqp.id, self.KEY_DONE)
        result = message_status == self.MESSAGE_DONE_YES
        self.debug('is done message: %s', result)
        return result

    def get_worker_id_by_message(self, message_amqp):
        if not message_amqp.id:
            return None
        key = self.get_key(message_amqp)
        worker_id = self.redis.hget(key, self.KEY_WORKER)
        return worker_id

    def get_key(self, message_amqp):
        return self.service_name + message_amqp.id

    def debug(self, msg, *args):
        self.logger.debug('Redis: ' + msg, *args)
