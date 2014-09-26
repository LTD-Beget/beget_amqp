# -*- coding: utf-8 -*-

import logging  # todo наследовать это


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

        return logging.getLogger(Logger.get_logger_name())

    @classmethod
    def critical(cls, *args, **kwargs):
        logger = Logger.get_logger()
        logger.critical(*args, **kwargs)
