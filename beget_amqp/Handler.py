# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import re


class Handler(object):
    logger = None

    def __init__(self):
        self.controller_prefix = ''

    def set_prefix(self, controller_prefix):
        self.controller_prefix = controller_prefix

    def on_message(self, message):
        try:
            result = self.run_controller(message)
            # message.success_callback(result)
        except Exception as e:
            self.logger.error(str(e))
            # message.failure_callback()

    def run_controller(self, message):
        controller_class = self._get_class(str(message.controller))
        target_controller = controller_class(message.action, logger=self.logger)
        method = getattr(target_controller, "run_action")

        return method(message.params)

    def _get_class(self, controller_name):
        target_module_name = "%s_controller" % self._from_camelcase_to_underscore(controller_name)
        target_cls_name = "%s%sController" % (controller_name[0].title(), controller_name[1:])
        controllers_module = sys.modules["%s.%s" % (self.controller_prefix, target_module_name)]
        controller_class = getattr(controllers_module, target_cls_name)

        return controller_class

    @staticmethod
    def _from_camelcase_to_underscore(string):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
