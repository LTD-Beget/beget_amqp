
import logging


class Logger():

    logger_name = 'beget_amqp'

    def __init__(self):
        pass

    @staticmethod
    def set_logger_name(name):
        Logger.logger_name = name

    @staticmethod
    def get_logger_name():
        return Logger.logger_name

    @staticmethod
    def get_logger(name=None):
        if name:
            Logger.set_logger_name(name)

        return logging.getLogger(Logger.get_logger_name())
