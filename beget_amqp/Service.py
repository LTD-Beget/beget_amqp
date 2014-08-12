# -*- coding: utf-8 -*-

from .lib.worker import AmqpWorker
from .lib.dependence.dependence_sync_manager import DependenceSyncManager
import time
import signal
import sys
from .lib.logger import Logger


class Service():

    STATUS_START = 1
    STATUS_STOP = 0

    def __init__(self,
                 host,
                 user,
                 password,
                 virtual_host,
                 queue,
                 number_workers=5,
                 port=5672,
                 durable=True,
                 auto_delete=False,
                 handler=None,
                 controllers_prefix=None,
                 logger_name=None
                 ):

        self.logger = Logger.get_logger(logger_name)

        if controllers_prefix is None and handler is None:
            raise Exception('Need set controllers_prefix or handler')

        if handler:
            if not 'on_message' in dir(handler):
                raise Exception('Handler must have a method - .on_message')
            self.handler = handler()
        else:
            from .Handler import Handler as AmqpHandler
            self.handler = AmqpHandler()

        if hasattr(self.handler, 'set_prefix'):
            self.handler.set_prefix(controllers_prefix)
        self.controller_callback = self.handler.on_message

        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.virtual_host = virtual_host
        self.queue = queue
        self.number_workers = number_workers
        self.durable = durable
        self.auto_delete = auto_delete

        self._status = self.STATUS_STOP
        self._worker_container = []
        self._last_worker_id = 0

        self.dependence_sync_manager = DependenceSyncManager.get_manager()

        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

    def sig_handler(self, signal, frame):
        self.logger.critical("Service: get signal %s and stop", signal)
        self.stop()
        sys.exit(1)

    def start(self):
        self.logger.info('Start service on host: %s,  port: %s,  VH: %s,  queue: %s',
                         self.host, self.port, self.virtual_host, self.queue)

        self._status = self.STATUS_START
        while True:
            while self.number_workers > len(self._worker_container) and self._status == self.STATUS_START:
                self.logger.debug('Service: Create worker-%s of %s', (len(self._worker_container) + 1), self.number_workers)
                worker = AmqpWorker(self.host,
                                    self.user,
                                    self.password,
                                    self.virtual_host,
                                    self.queue,
                                    self.controller_callback,
                                    self.dependence_sync_manager)
                worker.start()
                self._worker_container.append(worker)

            if self.number_workers < len(self._worker_container):
                self.logger.debug('Service: current count workers: %s but maximum: %s',
                                  len(self._worker_container),
                                  self.number_workers)

            self._delete_dead_workers()

            time.sleep(1)

    def _delete_dead_workers(self):
        for worker in self._worker_container:
            if not worker.is_alive():
                self._worker_container.remove(worker)
                self._delete_dead_workers()
                break

    def stop(self):
        self.logger.info('Service: stop Service')
        self._status = self.STATUS_STOP
        for worker in self._worker_container:
            if worker.is_alive():
                worker.terminate()
