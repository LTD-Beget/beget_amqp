# -*- coding: utf-8 -*-
import os

from multiprocessing.managers import BaseManager

import filelock

from .storage.dependence_storage_redis import DependenceStorageRedis
from ..helpers.logger import Logger

#
# Структура dict_of_queue:
# |dict Dependence_key_name:  # <-- имя зависимости
# |list     [0]:  #
# |dict         message_id: '123324345'  # <-- id сообщения которое ждет очереди
# |             worker_id: '3242323423432423' # <-- id воркера который поставил зависимость
#           [1]:
#               message_id: '234235345'
#               worker_id: '3242323423432423'
#           [2]:
#               message_id: '435657657'
#               worker_id: 'sdf3423r23423324'
#       Another_dependence_key_name:  # <-- Другкая зависимость (имена зависимостей не ограничены)
#           [0]:
#               message_id: '123324345'
#               worker_id: '3242323423432423'
#


class SyncManager(object):

    def __init__(self, amqp_vhost, amqp_queue):
        self.logger = Logger.get_logger()

        self.amqp_vhost = amqp_vhost
        self.amqp_queue = amqp_queue

        self.workers_id_list = []
        self.unacknowledged_message_id_list = []

        self.message_on_work = []
        self.consumer_worker_uid = None

        # avoid circular imports
        from beget_amqp import generate_uuid
        self.dependence_storage = DependenceStorageRedis(
            worker_id=generate_uuid(),
            amqp_vhost=self.amqp_vhost,
            amqp_queue=self.amqp_queue
        )

        self.logger.debug("SyncManager: creating file locks for '{}' amqp queue".format(self.amqp_queue))

        # avoid circular imports
        from beget_amqp import get_lockfile
        self.lock = filelock.FileLock(get_lockfile(
            'sync_manager:{}:{}'.format(
                self.amqp_vhost,
                self.amqp_queue
            )
        ))

        self.logger.debug("SyncManager: initialized and ready to work")

    def release_all_dependence_by_worker_id(self, worker_id):
        """
        Release all dependencies of worker
        :type worker_id: basestring
        """
        self.logger.critical('SyncManager: (dead worker?) release all dependence by worker id: %s', worker_id)
        self.dependence_storage.dependence_release_all_by_worker_id(worker_id)

    def check_status(self):
        """Заглушка для проверки связи"""
        return True

    def stop(self):
        # todo: Я не знаю, как еще можно завершить этот процесс, когда родительский процесс уже мертв.
        self.logger.critical('SyncManager: stop pid: %s', os.getpid())
        os.kill(os.getpid(), 9)

    @staticmethod
    def get_manager(amqp_vhost, amqp_queue):
        """
        :return: Объект менеджера передаваемый в multiprocessing воркеры
                 и предоставляющий общие ресурсы для всех воркеров
        :rtype: SyncManager
        """

        class CreatorSharedManager(BaseManager):
            SyncManager = None

        CreatorSharedManager.register('SyncManager', SyncManager)
        creator_shared_manager = CreatorSharedManager()
        creator_shared_manager.start()
        return creator_shared_manager.SyncManager(amqp_vhost, amqp_queue)  # ignore this warning of your IDE

    def get_workers_id(self):
        return self.workers_id_list

    def add_worker_id(self, worker_id):
        self.logger.debug('SyncManager: add worker id %s to list', worker_id)
        return self.workers_id_list.append(worker_id)

    def remove_worker_id(self, worker_id):
        self.logger.debug('SyncManager: remove worker id %s from list', worker_id)
        self.workers_id_list.remove(worker_id)

    def get_unacknowledged_message_id_list(self):
        return self.unacknowledged_message_id_list

    def add_unacknowledged_message_id(self, message_id):
        self.logger.debug('SyncManager: add unacknowledged message: %s', message_id)
        if message_id in self.unacknowledged_message_id_list:
            return False
        self.unacknowledged_message_id_list.append(message_id)
        return True

    def remove_unacknowledged_message_id(self, message_id):
        self.logger.debug('SyncManager: remove unacknowledged message: %s', message_id)
        if message_id not in self.unacknowledged_message_id_list:
            return False
        self.unacknowledged_message_id_list.remove(message_id)
        return True

    def get_message_on_work(self):
        return self.message_on_work

    def set_message_on_work(self, message_amqp):
        self.message_on_work.append(message_amqp.id)

    def set_message_on_work_done(self, message_amqp):
        self.message_on_work.remove(message_amqp.id)
