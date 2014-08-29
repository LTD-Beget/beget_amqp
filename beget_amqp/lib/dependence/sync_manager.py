# -*- coding: utf-8 -*-

import time
import sys
import datetime
import os

import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing import Lock

from ..logger import Logger


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

    def __init__(self):
        self.workers_id_list = []
        self.unacknowledged_message_id_list = []
        self.logger = Logger.get_logger()
        self.dict_of_queue = {}
        self.lock = Lock()

    def set_and_wait(self, message, worker_id=''):
        """
        :type message: MessageAmqp
        :type worker_id: basestring
        """
        self.set(message, worker_id)
        self.wait(message)

    def wait(self, message):
        """
        infinity loop until I got permission to continue
        :type message: MessageAmqp
        """
        self.logger.debug('SyncManager: wait-dependence: %s', repr(message.dependence))
        while True:
            if self.is_available_dependence(message):
                return True
            time.sleep(0.1)

    def is_available_dependence(self, message):
        """
        Check whether our turn
        :type message: MessageAmqp
        """
        for dep in message.dependence:
            if not dep in self.dict_of_queue:
                continue
            dependence_current = self.dict_of_queue[dep][0]

            # compare our id with id first in queue
            if message.id != dependence_current['message_id']:
                return False
        return True

    def set(self, message, worker_id=''):
        """
        Set our dependencies in queue
        :type message: MessageAmqp
        :type worker_id: basestring
        """
        self.logger.debug('SyncManager: set-dependence: %s, worker_id: %s', repr(message.dependence), worker_id)
        self.lock.acquire()  # in one moment only one worker may write dependence. Otherwise we may get deadlock.
        for dep in message.dependence:
            if dep in self.dict_of_queue:
                # if we have queue by dependence name, we add id in queue
                self.dict_of_queue[dep].append(dict(message_id=message.id, worker_id=worker_id))
            else:
                self.dict_of_queue[dep] = [dict(message_id=message.id, worker_id=worker_id)]
        self.lock.release()

    def release(self, message):
        """
        Release our dependencies from queue
        :type message: MessageAmqp
        """
        self.logger.debug('SyncManager: release-dependence: %s', repr(message.dependence))
        for dependence_name in message.dependence:
            if not dependence_name in self.dict_of_queue:
                continue
            dependence_list = self.dict_of_queue[dependence_name]
            for dependence in dependence_list[:]:
                if not message.id == dependence.get('message_id'):
                    continue
                dependence_list.remove(dependence)

    def release_all_dependence_by_worker_id(self, worker_id):
        """
        Release all dependencies of worker
        :type worker_id: basestring
        """
        self.logger.critical('SyncManager: (dead worker?) release all dependence by worker id: %s', worker_id)
        for dependence_list in self.dict_of_queue.values():
            for dependence in dependence_list[:]:
                if not worker_id == dependence.get('worker_id'):
                    continue
                dependence_list.remove(dependence)

    def check_status(self):
        """Заглушка для проверки связи"""
        return True

    def stop(self):
        # todo: Я не знаю, как еще можно завершить этот процесс, когда родительский процесс уже мертв.
        self.logger.critical('SyncManager stop pid: %s', os.getpid())
        os.kill(os.getpid(), 9)

    @staticmethod
    def get_manager():
        """
        :return: Объект менеджера передаваемый в multiprocessing воркеры
                 и предоставляющий общие ресурсы для всех воркеров
        :rtype: SyncManager
        """

        class CreatorSharedManager(BaseManager):
            pass

        CreatorSharedManager.register('SyncManager', SyncManager)
        creator_shared_manager = CreatorSharedManager()
        creator_shared_manager.start()
        return creator_shared_manager.SyncManager()

    def get_workers_id(self):
        return self.workers_id_list

    def add_worker_id(self, worker_id):
        self.logger.debug('SyncManager: Add worker id %s to list', worker_id)
        return self.workers_id_list.append(worker_id)

    def remove_worker_id(self, worker_id):
        self.logger.debug('SyncManager: remove worker id %s from list', worker_id)
        self.workers_id_list.remove(worker_id)

    def get_unacknowledged_message_id_list(self):
        return self.unacknowledged_message_id_list

    def add_unacknowledged_message_id(self, id):
        self.logger.debug('SyncManager: add unacknowledged message:', id)
        if id in self.unacknowledged_message_id_list:
            return False
        self.unacknowledged_message_id_list.append(id)
        return True

    def remove_unacknowledged_message_id(self, id):
        self.logger.debug('SyncManager: remove unacknowledged message:', id)
        if id not in self.unacknowledged_message_id_list:
            return False
        self.unacknowledged_message_id_list.remove(id)
        return True
