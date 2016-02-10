# -*- coding: utf-8 -*-

import time
import signal
import sys
import os
import traceback
import uuid

from .lib.helpers.logger import Logger
from .lib.worker import AmqpWorker
from .lib.dependence.sync_manager import SyncManager
from .Sender import Sender
from .lib.communicate.comunicate_redis import CommunicateRedis
from ._version import __version__ as version


class Service():
    """
    Класс который позволяет Вам запустить свою RPC поверх AMQP.
    Работа по средством использования контроллеров.
    """

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
                 prefetch_count=1,
                 durable=True,
                 auto_delete=False,
                 handler=None,
                 controllers_prefix=None,
                 logger_name=None,
                 no_ack=False,
                 max_la=0):
        """
        :param host:  может принимать как адрес, так и hostname, так и '' для прослушки всех интерфейсов.
        :param user:
        :param password:
        :param virtual_host:
        :param queue:
        :param number_workers:  Количество воркинг процессов которое поддерживается во время работы
        :param port:
        :param prefetch_count:  Количество получаемых сообщений за один раз из AMQP.

        :param durable:  При создание, очередь назначается 'устойчивой',
                         что позволяет не терять соббщения при перезапуске AMQP сервера

        :param auto_delete:  При создание, очередь назначается 'авто-удаляемой',
                             что позволяет удалять очередь когда в ней нет сообщений

        :param handler:  Можно передать кастомный обработчик который будет получать сообщения из AMQP

        :param controllers_prefix:  Префикс контроллеров (имя в sys.modules)
                                    который будет использоваться при поиске контроллера

        :param logger_name:  Имя для логирования
        :param no_ack:  Игнорировать необходимость подтверждения сообщений.
                        (Все сообщения сразу будут выданы работникам, даже если они заняты)

        :param max_la: При каком load average на сервере приостанавливать выполнение заданий, <= 0 - выключено
        """
        # Получаем логгер в начале, иначе другие классы могут получить другое имя для логера
        self.logger = Logger.get_logger(logger_name)

        # Если передали кастомный хэндлер, то используем его
        if controllers_prefix is None and handler is None:
            raise Exception('Need set controllers_prefix or handler')
        if handler:
            if 'on_message' not in dir(handler):
                raise Exception('Handler must have a method - .on_message')
            self.handler = handler()
        else:
            from .Handler import Handler as AmqpHandler
            self.handler = AmqpHandler()

        # Сообщаем хендлеру префикс контроллеров
        if hasattr(self.handler, 'set_prefix'):
            self.handler.set_prefix(controllers_prefix)

        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.prefetch_count = prefetch_count
        self.virtual_host = virtual_host
        self.queue = queue
        self.number_workers = number_workers
        self.durable = durable
        self.auto_delete = auto_delete
        self.no_ack = no_ack

        self._status = self.STATUS_STOP
        self._worker_container = []
        self._worker_id_list_in_killed_process = []
        """:type : list[AmqpWorker]"""
        self._last_worker_id = 0

        self.communicator = CommunicateRedis(self.queue)
        self.sync_manager = SyncManager.get_manager()
        self.sender = Sender(user, password, host, port, virtual_host)

        self.max_la = max_la

        # Ctrl+C приводит к немедленной остановке
        signal.signal(signal.SIGINT, self.sig_handler)

        # 15 и 1 сигнал приводят к мягкой остановке
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGHUP, self.sig_handler)

    def start(self):
        """
        Запускаем сервис
        """
        self.debug('pid: %s', os.getpid())
        self.info('Start service on host: %s,  port: %s,  VH: %s,  queue: %s version: %s',
                  self.host, self.port, self.virtual_host, self.queue, version)
        self._status = self.STATUS_START

        # Основной бесконечный цикл. Выход через сигналы или Exception
        while self._status == self.STATUS_START:

            message_nack_list = self.sync_manager.get_unacknowledged_message_id_list()
            worker_required_number = self.number_workers + len(message_nack_list)

            # Если воркеров меньше чем положено, создаем новых.
            while worker_required_number > self.get_workers_alive_count():
                self.debug('Create worker-%s of %s',
                           (len(self._worker_container) + 1), self.number_workers)

                uid = self.generate_uid()

                worker = AmqpWorker(self.host,
                                    self.user,
                                    self.password,
                                    self.virtual_host,
                                    self.queue,
                                    self.handler,
                                    self.sync_manager,
                                    self.port,
                                    no_ack=self.no_ack,
                                    prefetch_count=self.prefetch_count,
                                    uid=uid,
                                    sender=self.sender,
                                    max_la=self.max_la)
                worker.start()
                self._worker_container.append(worker)
                self.sync_manager.add_worker_id(worker.uid)

            if worker_required_number < self.get_workers_alive_count():
                self.debug('current count workers: %s but maximum: %s',
                           len(self._worker_container), self.number_workers)
                self.stop_one_worker()

            # Если воркер умер, убераем его из расчета.
            self._delete_dead_workers()

            # обработка запросов в API для пакета
            self.communicate()

            # Снижение скорости проверки воркеров
            time.sleep(1)

    def _delete_dead_workers(self):
        """
        Удаление мертвых воркеров.
        """
        for worker in self._worker_container:
            if worker.is_alive():
                continue
            self.sync_manager.release_all_dependence_by_worker_id(worker.uid)
            self.sync_manager.remove_worker_id(worker.uid)
            self.sync_manager.clear_consume()
            if worker.uid in self._worker_id_list_in_killed_process:
                self._worker_id_list_in_killed_process.remove(worker.uid)
            self._worker_container.remove(worker)
            self._delete_dead_workers()
            break

    def sig_handler(self, sig_num, frame):
        """
        Обрабатываем сигналы
        """
        self.debug('get signal %s', sig_num)
        if sig_num is signal.SIGHUP or sig_num is signal.SIGTERM:
            self.clean_signals()
            self.stop_smoothly()

        if sig_num is signal.SIGINT:
            self.clean_signals()
            self.stop_immediately()

    def clean_signals(self):
        """
        Отключаем обработку сигналов
        """
        self.debug('stop receiving signals')
        signal.signal(signal.SIGINT, self.debug_signal)
        signal.signal(signal.SIGTERM, self.debug_signal)
        signal.signal(signal.SIGHUP, self.debug_signal)

    def debug_signal(self, sig_num, frame):
        """
        Метод-заглушка для сигналов
        """
        self.debug('get signal %s but not handle this.', sig_num)

    def stop(self):
        """
        Останавливаем сервисы
        """
        self.info('stop Service')
        self.stop_smoothly()

    def stop_immediately(self):
        """
        Жесткая остановка
        """
        self.critical('stop immediately')

        try:
            # Убиваем воркеров
            for worker in self._worker_container:
                if not worker.is_alive():
                    continue
                worker.terminate()
        except Exception as e:
            self.debug('when terminate worker: Exception: %s\n  %s', e.message, traceback.format_exc())
        # Выходим
        sys.exit(1)

    def stop_smoothly(self):
        """
        Плавная остановка с разрешением воркерам доделать свою работу
        """
        self.critical('smoothly stops workers and exit')

        # Посылаем всем воркерам сигнал плавного завершения
        for worker in self._worker_container:
            try:
                if not worker.is_alive():
                    continue
                os.kill(worker.pid, signal.SIGHUP)
            except Exception as e:
                self.debug('when send signal to worker: Exception: %s\n  %s', e.message, traceback.format_exc())

        # Ждем пока все воркеры остановятся
        for worker in self._worker_container:
            try:
                if not worker.is_alive():
                    continue
                self.debug('wait when %s is die' % repr(worker))
                worker.join()
            except Exception as e:
                self.debug('when wait worker: Exception: %s\n  %s', e.message, traceback.format_exc())

        # Выходим
        self._status = self.STATUS_STOP

    @staticmethod
    def generate_uid():
        return str(uuid.uuid4())

    def get_workers_alive_count(self):
        workers_alive_count = len(self._worker_container) - len(self._worker_id_list_in_killed_process)
        return workers_alive_count

    def stop_one_worker(self):
        for worker in self._worker_container:
            try:
                if not worker.is_alive():
                    continue
                if worker.uid in self._worker_id_list_in_killed_process:
                    continue
                os.kill(worker.pid, signal.SIGHUP)
                self._worker_id_list_in_killed_process.append(worker.uid)
                return True

            except Exception as e:
                self.debug('when send signal to worker: Exception: %s\n  %s', e.message, traceback.format_exc())
        return False

    def add_transport(self, transport, transport_name):
        """
        Добавление транспорта, который может использовать Sender.

        :param transport: Объект транспорта, который содержит метод send
        :param transport_name: Имя-ключ транспорта, по которому мы получаем его
        :type transport_name: basestring
        """
        self.sender.add_transport(transport, transport_name)

    def communicate(self):
        question_list = self.communicator.get_question_list()
        if not isinstance(question_list, dict):
            return None

        for question_key, question in question_list.iteritems():
            self.debug('get question: %s', question)
            answer = self.answer_for_question(question)
            self.communicator.set_answer(question_key, answer)

    def answer_for_question(self, question):
        method_name = 'action_' + question
        method = getattr(self, method_name, None)
        if not method:
            return 'Not find method: ' + method_name

        try:
            return method()
        except Exception as e:
            self.debug('when answered to question: Exception: %s\n  %s', e.message, traceback.format_exc())
            return 'Error in method'

    def action_ping(self):
        return 'pong'

    def action_get_current_status(self):
        """
        Возвращаем информацию о текущей деятельности:
          - id сообщений которые находятся в работе
          - количество воркеров
        """
        return {
            'worker_number': self.get_workers_alive_count(),
            'message_list': self.sync_manager.get_message_on_work()
        }

    def action_shutdown(self):
        """
        Плавная остановка сервера.
        """
        self.logger.info('Shutting down by request from api')
        self.clean_signals()
        self.stop_smoothly()
        return 'Ok'

    def debug(self, msg, *args):
        self.logger.debug('Service: ' + msg, *args)

    def info(self, msg, *args):
        self.logger.info('Service: ' + msg, *args)

    def critical(self, msg, *args):
        self.logger.critical('Service: ' + msg, *args)
