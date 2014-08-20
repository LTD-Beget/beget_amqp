# -*- coding: utf-8 -*-

from multiprocessing import Process
from .message_constructor import MessageConstructor
from .listen import AmqpListen
from .logger import Logger
import signal
import os
import sys
import traceback
import socket


class AmqpWorker(Process):

    WORKING_YES = True  # Воркер занимается выполнением задачи
    WORKING_NOT = False  # Воркер не выполняет задач

    STATUS_START = True  # Воркер продолжает работу
    STATUS_STOP = False  # Воркер завершает работу

    def __init__(self,
                 host,
                 user,
                 password,
                 virtual_host,
                 queue,
                 callback,
                 sync_manager,
                 port=5672,
                 durable=True,
                 auto_delete=False,
                 no_ack=False,
                 prefetch_count=1,
                 uid=''):
        Process.__init__(self)

        self.logger = Logger.get_logger()
        self.host = host
        self.user = user
        self.password = password
        self.virtual_host = virtual_host
        self.queue = queue
        self.callback = callback
        self.sync_manager = sync_manager
        """:type : beget_amqp.lib.dependence.sync_manager.SyncManager"""
        self.port = port
        self.durable = durable
        self.auto_delete = auto_delete
        self.no_ack = no_ack
        self.prefetch_count = prefetch_count
        self.uid = uid

        # обнуляем
        self.amqp_listener = None
        self.current_message = None  # Для хранения обрабатываемого сообщения
        self.working_status = self.WORKING_NOT  # Получили и работаем над сообщением?
        self.program_status = self.STATUS_START  # Программа должна выполняться и дальше? (Для плавного выхода)

    def run(self):
        """
        Начинаем работать в качестве отдельного процесса.
        """
        self._name = self._name + '(' + str(os.getpid()) + ')'
        # Назначаем сигналы для выхода
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGHUP, self.sig_handler)

        # Начинаем слушать AMQP и выполнять задачи полученные из сообщений:
        try:
            self.amqp_listener = AmqpListen(self.host,
                                            self.user,
                                            self.password,
                                            self.virtual_host,
                                            self.queue,
                                            self._on_message,
                                            self.port,
                                            self.durable,
                                            self.auto_delete,
                                            self.no_ack,
                                            self.prefetch_count)
            self.amqp_listener.start()
        except Exception as e:
            self.error('Exception: %s\n'
                       '  %s\n', e.message, traceback.format_exc())

        self.debug('Correct exit from multiprocessing')

    def _on_message(self, channel, method, properties, body):
        """
        Обрабатываем сообщение полученное из AMQP

        :param channel:  канал подключения.
        :type channel: pika.adapters.blocking_connection.BlockingChannel

        :param method:  метод
        :type method: pika.spec.Deliver

        :param properties: параметры сообщения
        :type properties: pika.spec.BasicProperties

        :param body: тело сообщения
        :type body: basestring
        """
        self.check_allowed_to_live()

        self.debug('get message:\n'
                   '  properties: %s\n'
                   '  method: %s\n'
                   '  body: %s', repr(properties), repr(method), repr(body))

        # Получаем объект сообщения из сырого body
        message_constructor = MessageConstructor()
        message_amqp = message_constructor.create_message_amqp(properties, body)
        message_to_service = message_constructor.create_message_to_service_by_message_amqp(message_amqp)

        # Устанавливаем зависимости сообщения
        self.set_dependence(message_amqp)
        try:
            self.debug('Wait until the dependence be free')
            self.wait_dependence(message_amqp)
            self.debug('Execute callback')
            self.working_status = self.WORKING_YES
            self.callback(message_to_service)
        except Exception as e:
            self.error('Exception: %s\n'
                       '  %s', e.message, traceback.format_exc())

        self.debug('Report to AMQP about message being receive')
        channel.basic_ack(delivery_tag=method.delivery_tag)
        self.release_dependence(message_amqp)
        self.working_status = self.WORKING_NOT

        # Если за время работы над сообщением мы получили команду выхода, то выходим
        self.check_allowed_to_live()

    def set_dependence(self, message_amqp):
        """
        Ставим зависимость сообщения в очередь.
        :type message_amqp: MessageAmqp
        """
        if not message_amqp.dependence:
            return
        try:
            self.sync_manager.set(message_amqp, self.uid)
        except socket.error:
            self.handler_error_sync_manager()

    def wait_dependence(self, message_amqp):
        """
        Ожидаем пока зависимость освободится
        :type message_amqp: MessageAmqp
        """
        if not message_amqp.dependence:
            return
        try:
            self.sync_manager.wait(message_amqp)
        except (IOError, EOFError):
            self.handler_error_sync_manager()

    def release_dependence(self, message_amqp):
        """
        Освобождаем зависимость
        :type message_amqp: MessageAmqp
        """
        if not message_amqp.dependence:
            return
        try:
            self.sync_manager.release(message_amqp)
        except (IOError, EOFError):
            self.handler_error_sync_manager()

    def sig_handler(self, sig_num, frame):
        """
        Обработчик сигналов
        """
        self.debug('get signal %s', sig_num)
        if sig_num is signal.SIGHUP or sig_num is signal.SIGTERM:
            self.stop()

    ################################################################################
    # Функции обработки аварийных ситуация и выхода

    def check_allowed_to_live(self):
        """
        Проверяем разрешение на продолжение работы и обработываем ситуацию аварийного выхода
        """
        if self.program_status is self.STATUS_STOP:
            self.stop()

        if not self.is_main_process_alive():
            self.handler_error_main_process()

        if not self.is_sync_manager_alive():
            self.handler_error_sync_manager()

        return True

    def is_main_process_alive(self):
        """
        Жив ли основной процесс
        """
        if os.getppid() == 1:
            return False
        return True

    def is_sync_manager_alive(self):
        """
        Жив ли SyncManager
        """
        try:
            self.sync_manager.check_status()
            return True
        except:
            return False

    def handler_error_sync_manager(self):
        """
        Обработчик ситуации, когда SyncManager мертв
        """
        self.critical('SyncManager is dead, but i\'m alive. Program quit')
        if self.is_main_process_alive():
            os.kill(os.getppid(), signal.SIGHUP)
        self.stop()

    def handler_error_main_process(self):
        """
        Обработчик ситуации, когда основной процесс мертв
        """
        self.critical('Main process is dead, but i\'m alive. Program quit')
        try:
            self.sync_manager.stop()
        except:
            pass
        self.stop()

    def stop(self):
        """
        Корректное завершение
        """
        if self.working_status is self.WORKING_NOT:
            self.debug('immediately exit')
            os.kill(os.getpid(), 9)  # todo корректный выход
            # self.amqp_listener.stop()
        else:
            self.debug('stop when the work will be done')
            self.program_status = self.STATUS_STOP

    ################################################################################
    # Логирование

    def debug(self, msg, *args):
        self.logger.debug('%s: ' + msg, self._name, *args)

    def info(self, msg, *args):
        self.logger.info('%s: ' + msg, self._name, *args)

    def critical(self, msg, *args):
        self.logger.critical('%s: ' + msg, self._name, *args)

    def error(self, msg, *args):
        self.logger.error('%s: ' + msg, self._name, *args)

