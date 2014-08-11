# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import re
import logging
import traceback


class Handler(object):

    def __init__(self):
        self.logger = logging.getLogger('beget_amqp')
        self.controller_prefix = ''

    def set_prefix(self, controller_prefix):
        self.controller_prefix = controller_prefix

    def on_message(self, message):
        try:
            result = self.run_controller(message)
            # message.success_callback(result)
        except Exception as e:
            self.logger.error('Handler->on_message: Exception: %s\n'
                              'Traceback: %s', e.message, traceback.format_exc())
            # message.failure_callback()

    def run_controller(self, message):
        self.logger.debug('Handler->run_controller: get message: %s', repr(message))
        controller_class = self._get_class(str(message.controller))

        self.logger.debug('Handler: use action: %s', message.action)
        target_controller = controller_class(message.action)
        method = getattr(target_controller, "run_action")

        return method(message.params)

    def _get_class(self, controller_name):
        target_module_name = "%s_controller" % self._from_camelcase_to_underscore(controller_name)
        target_cls_name = "%s%sController" % (controller_name[0].title(), controller_name[1:])
        full_controller_name = "%s.%s" % (self.controller_prefix, target_module_name)
        self.logger.debug('Handler: get module controller: %s', full_controller_name)
        self.logger.debug('Handler: get class controller: %s', target_cls_name)
        controllers_module = sys.modules[full_controller_name]
        controller_class = getattr(controllers_module, target_cls_name)

        return controller_class

    @staticmethod
    def _from_camelcase_to_underscore(string):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
