# -*- coding: utf-8 -*-

import logging  # todo наследовать это
import uuid
import time


class LoggerAdapterRequestId(logging.LoggerAdapter):
    """
    Предоставляет обертку для лога, отвечающую за работу с uid
    """

    def request_id_generate(self):
        self.logger.request_id = str(uuid.uuid4())[:8]

    def request_id_clear(self):
        self.logger.request_id = ''

    def process(self, msg, kwargs):
        if hasattr(self.logger, 'request_id') and self.logger.request_id:
            return '[id:%s] %s' % (self.logger.request_id, msg), kwargs
        return msg, kwargs


class Logger():
    """
    Класс для логирования.
    Хранит состояние имени
    """

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG

    logger_name = 'beget.amqp'  # Имя лога которое будет использоваться по модулю

    def __init__(self):
        pass

    @staticmethod
    def set_logger_name(name):
        """
        Переопределение имени
        """
        Logger.logger_name = name

    @staticmethod
    def get_logger_name():
        """
        Получение имени
        """
        return Logger.logger_name

    @staticmethod
    def get_logger(name=None):
        """
        Получить объект логгера. Опционально - задать имя логирования
        """
        if name:
            Logger.set_logger_name(name)

        return LoggerAdapterRequestId(logging.getLogger(Logger.get_logger_name()), {})

    @classmethod
    def critical(cls, *args, **kwargs):
        logger = Logger.get_logger()
        logger.critical(*args, **kwargs)


def uid_logger_wrapper_method(func):
    """
    Оберткка для метода добавляющая uid к логам и время выполнения функции
    Необходимо наличие LoggerAdapterRequestId в self.logger
    """

    def wrapper(*args, **kwargs):
        time_start = time.time()

        self = args[0]
        self.logger.request_id_generate()

        try:
            func(*args, **kwargs)
        finally:
            self.logger.debug('Request completed in seconds: %s', time.time() - time_start)
            self.logger.request_id_clear()

    return wrapper
