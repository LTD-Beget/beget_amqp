# -*- coding: utf-8 -*-
import filelock

from .storage_redis import StorageRedis


class ConsumerStorageRedis(StorageRedis):
    """
    Локальное хранение информации о консьюмерах
    """

    def __init__(self, worker_id, amqp_vhost, amqp_queue, redis_socket="/var/run/redis/redis.sock"):
        super(ConsumerStorageRedis, self).__init__(redis_socket)
        self.worker_id = worker_id
        self.amqp_vhost = amqp_vhost
        self.amqp_queue = amqp_queue

        # avoid circular imports
        from beget_amqp import get_lockfile
        self.lock = filelock.FileLock(get_lockfile(self.get_consumer_key()))

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
        return '{}:{}:{}'.format(self.CONSUMER_PREFIX, self.amqp_vhost, self.amqp_queue)

    def debug(self, msg, *args):
        self.logger.debug('RedisConsumerStorage: ' + msg, *args)
