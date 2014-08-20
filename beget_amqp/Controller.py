# -*- coding: utf-8 -*-

from .lib.logger import Logger
import traceback


class Controller(object):
    """
    Базовый класс для контроллеров
    """
    def __init__(self, action_name):
        self.action_name = action_name
        self.logger = Logger.get_logger()

    def run_action(self, params):
        action_name = "action_%s" % str(self.action_name)
        action_method = getattr(self, action_name)

        self.logger.info('Controller Exec: %s.%s(%s)', self.__class__.__name__, action_name, repr(params))
        try:
            result = action_method(**params)
            return result
        except Exception as e:
            self.logger.error('Controller Error in action: %s\n  %s', e.message, traceback.format_exc())

