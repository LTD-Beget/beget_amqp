# -*- coding: utf-8 -*-
import json
import time
import sys

import filelock

from .storage_redis import StorageRedis


class DependenceStorageRedis(StorageRedis):
    """
    Локальное хранение сообщений и информации о нем.
    """

    LOCKFILE_TEMPLATE = '/var/run/dependence:{}:{}.lock'

    def __init__(self, worker_id, queue, socket="/var/run/redis/redis.sock"):
        super(DependenceStorageRedis, self).__init__(socket)
        self.worker_id = worker_id
        self.queue = queue

    def get_dependence_lockfile(self, dependence_name):
        lockfile = self.LOCKFILE_TEMPLATE.format(self.queue, dependence_name)
        return lockfile

    def dependence_set(self, message):
        """
        :param message:
        :type message: MessageAmqp

        :return:
        """

        self.debug(
            'set-dependence: {} for message {} by worker {}'.format(message.dependence, message.id, self.worker_id))

        for dependence_name in message.dependence:
            lock = filelock.FileLock(self.get_dependence_lockfile(dependence_name))
            lock.acquire()

            key = self.get_dependence_key(dependence_name)
            self.debug('set-dependence: name={}, key={}'.format(dependence_name, key))

            self.redis.rpush(key, json.dumps(dict(message_id=message.id, worker_id=self.worker_id)))

            lock.release()

    def dependence_release(self, message):
        """
        :param message:
        :type message: MessageAmqp

        :return:
        """

        self.debug(
            'release-dependence: {} for message {} by worker {}'.format(message.dependence, message.id, self.worker_id))

        for dependence_name in message.dependence:
            lock = filelock.FileLock(self.get_dependence_lockfile(dependence_name))
            lock.acquire()

            key = self.get_dependence_key(dependence_name)
            self.debug('release-dependence: name={}, key={}'.format(dependence_name, key))

            dependence_list = self.redis.lrange(key, 0, -1)

            for dependence_json in dependence_list:
                dependence = json.loads(dependence_json)
                if message.id == dependence['message_id']:
                    self.redis.lrem(key, 0, dependence_json)

            lock.release()

    def dependence_release_all_by_worker_id(self, worker_id=None):
        if worker_id is None:
            worker_id = self.worker_id

        self.debug('release-all-dependencies for worker {}'.format(worker_id))

        dependence_names = self.get_all_dependence_names()

        for dependence_name in dependence_names:
            lock = filelock.FileLock(self.get_dependence_lockfile(dependence_name))
            lock.acquire()

            key = self.get_dependence_key(dependence_name)
            self.debug('release-all-dependencies: name={}, key={}'.format(dependence_name, key))

            dependence_list = self.redis.lrange(key, 0, -1)

            for dependence_json in dependence_list:
                dependence = json.loads(dependence_json)
                if worker_id == dependence['worker_id']:
                    self.redis.lrem(key, 0, dependence_json)

            lock.release()

    def get_all_dependence_names(self):
        dependence_names = self.redis.keys('{}:{}:*'.format(self.DEPENDENCE_PREFIX, self.queue))
        return dependence_names

    def get_dependence_key(self, dependence_name):
        return '{}:{}:{}'.format(self.DEPENDENCE_PREFIX, self.queue, dependence_name)

    def debug(self, msg, *args):
        self.logger.debug('RedisDependenceStorage: ' + msg, *args)

    def dependence_is_available(self, message):
        """
        :param message:
        :type message: MessageAmqp

        :return:
        """
        # avoid circular imports
        from beget_amqp.lib.worker import AmqpWorker

        available_status = {}

        self.debug(
            'wait-dependence: testing message {} with dependence {}'.format(message.id, message.dependence))

        for dependence_name in message.dependence:
            available_status[dependence_name] = True

            lock = filelock.FileLock(self.get_dependence_lockfile(dependence_name))
            lock.acquire()

            key = self.get_dependence_key(dependence_name)
            self.debug('wait-dependence: name={}, key={}'.format(dependence_name, key))

            dependence_list = self.redis.lrange(key, 0, -1)
            self.debug('wait-dependence: start dependence_list={}'.format(dependence_list))

            for dependence_json in dependence_list:
                dependence = json.loads(dependence_json)
                if not AmqpWorker.is_worker_alive(dependence['worker_id']):
                    self.redis.lrem(key, 0, dependence_json)

            dependence_list = self.redis.lrange(key, 0, -1)
            self.debug('wait-dependence: end dependence_list={}'.format(dependence_list))

            for dependence_json in dependence_list:
                dependence = json.loads(dependence_json)
                self.debug('wait-dependence: current dependence={}'.format(dependence))
                if message.id != dependence['message_id']:
                    available_status[dependence_name] = False

                # we care about only first message_id here
                break

            lock.release()

        self.debug('wait-dependence: available-status={}'.format(available_status))

        is_available = all(available_status.values())
        self.debug('wait-dependence: {} final status is {}'.format(message.dependence, is_available))

        return is_available