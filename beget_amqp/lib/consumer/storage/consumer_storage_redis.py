# -*- coding: utf-8 -*-
import json
import time
import sys

import filelock

from .storage_redis import StorageRedis


class ConsumerStorageRedis(StorageRedis):
    """
    Локальное хранение информации о консьюмерах
    """

    LOCKFILE_TEMPLATE = '/var/run/consumer:{}.lock'

    def __init__(self, worker_id, queue, socket="/var/run/redis/redis.sock"):
        super(ConsumerStorageRedis, self).__init__(socket)
        self.worker_id = worker_id
        self.queue = queue
        self.lock = filelock.FileLock(self.LOCKFILE_TEMPLATE.format(self.queue))

    def consumer_release(self):
        self.lock.acquire()

        key = self.get_consumer_key()
        worker_id = self.redis.get(key)

        self.debug('clear-consumer: current consumer was {}'.format(worker_id))
        self.redis.set(key, '')

        self.lock.release()

    def consumer_is_allowed(self):
        is_allowed = False

        self.lock.acquire()

        key = self.get_consumer_key()
        worker_id = self.redis.get(key)

        if not worker_id:
            self.redis.set(key, self.worker_id)
            is_allowed = True
            self.debug(
                'allow-consumer: no current consumer, allow current worker {} to become consumer'.format(
                    self.worker_id
                )
            )

        elif worker_id == self.worker_id:
            is_allowed = True
            self.debug('allow-consumer: current worker {} is consumer'.format(worker_id))

        else:
            # avoid circular imports
            from beget_amqp.lib.worker import AmqpWorker
            if not AmqpWorker.is_worker_alive(worker_id):
                self.redis.set(key, self.worker_id)
                is_allowed = True
                self.debug(
                    'allow-consumer: current consumer is dead (was {}), allow current worker to become consumer'.format(
                        self.worker_id
                    )
                )

        self.lock.release()

        return is_allowed

    def get_consumer_key(self):
        return '{}:{}'.format(self.CONSUMER_PREFIX, self.queue)

    def debug(self, msg, *args):
        self.logger.debug('RedisConsumerStorage: ' + msg, *args)
