# -*- coding: utf-8 -*-

import traceback

from .lib.helpers.logger import Logger
from .lib.exception.ExceptionAction import ExceptionAction
from .lib.exception.ExceptionHandler import ExceptionHandler
from .lib.exception.CallbackData import CallbackData


class Controller(object):
    """
    Базовый класс для контроллеров
    """
    def __init__(self, action_name):
        self.action_name = action_name
        self.logger = Logger.get_logger()

    def run_action(self, params):
        action_name = "action_%s" % str(self.action_name)

        try:
            action_method = getattr(self, action_name)
        except AttributeError:
            # Ситуация, когда контроллер успешно выбран, но такого action в нем нет.
            raise ExceptionHandler(
                'Controller "%s" has not action "%s"' % (self.__class__.__name__, action_name),
                trace=traceback.format_exc()
            )

        self.logger.info('Controller: Exec: %s.%s(%s)', self.__class__.__name__, action_name, repr(params))
        try:
            return action_method(**params)
        except CallbackData as e:
            # Данные для callback игнорируем и прокидываем дальше, предположительно до worker
            raise e

        except Exception as e:
            # Все ошибки Action пакуем в наш формат и прокидываем наверх, чтобы вызывать callback
            self.logger.error('Controller: exception in action: %s', e)
            raise ExceptionAction(
                e.args[0] if len(e.args) and isinstance(e.args[0], basestring) else str(e),
                e.args[1] if len(e.args) > 1 and isinstance(e.args[1], int) else 1,
                e.trace if hasattr(e, 'trace') else traceback.format_exc()
            )

    def run_after_action(self):
        """
        Для переопределения
         - запускается не зависимо от возникновение ошибки в run_action
         - return  и возникновение ошибок игнорируется
        """
        pass
