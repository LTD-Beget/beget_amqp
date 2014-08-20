# -*- coding: utf-8 -*-

import sys
import re
import traceback
from .lib.logger import Logger


class Handler(object):
    """
    Обработчик сообщений
    Получает AMQP сообщение, преобразовывает его и передает необходимому контроллеру.
    """

    def __init__(self):
        self.logger = Logger.get_logger()
        self.controller_prefix = ''

    def set_prefix(self, controller_prefix):
        """
        :param controller_prefix: Указывает префикс sys.modules в котором следует искать контроллер
        """
        self.controller_prefix = controller_prefix

    def on_message(self, message):
        """
        Получаем сообщение
        :type message: MessageAmqp
        """
        try:
            result = self.run_controller(message)
            # message.success_callback(result)
        except Exception as e:
            self.logger.error('Handler->on_message: Exception: %s\n'
                              '  %s', e.message, traceback.format_exc())
            # message.failure_callback()

    def run_controller(self, message):
        """
        вызываем контроллер с переданными в сообщение параметрами.
        :type message: MessageAmqp
        """
        self.logger.debug('Handler: get message: %s', repr(message))
        controller_class = self._get_class(str(message.controller))

        self.logger.debug('Handler: use:\n'
                          '  action: %s\n'
                          '  params: %s', message.action, message.params)
        target_controller = controller_class(message.action)
        method = getattr(target_controller, "run_action")

        return method(message.params)

    def _get_class(self, controller_name):
        """
        Ищем и возвращаем запрошенный класс
        """
        target_module_name = "%s_controller" % self._from_camelcase_to_underscore(controller_name)
        target_cls_name = "%s%sController" % (controller_name[0].title(), controller_name[1:])
        full_controller_name = "%s.%s" % (self.controller_prefix, target_module_name)
        self.logger.debug('Handler: use:\n'
                          '  module of controller: %s\n'
                          '  class in controller: %s', full_controller_name, target_cls_name)
        controllers_module = sys.modules[full_controller_name]
        controller_class = getattr(controllers_module, target_cls_name)

        return controller_class

    @staticmethod
    def _from_camelcase_to_underscore(string):
        """
        In: hello
        Out: hello

        In: helloWorld
        Out: hello-world

        In: HELLOWORLD
        Out: helloworld

        In: HelloMyFrendFromSpace
        Out: -hello-my-frend-from-space
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
