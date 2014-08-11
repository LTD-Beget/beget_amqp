import logging


class Controller(object):
    def __init__(self, action_name):
        self.action_name = action_name
        self.logger = logging.getLogger('beget_amqp')

    def run_action(self, params):
        action_name = "action_%s" % str(self.action_name)
        action_method = getattr(self, action_name)

        self.logger.debug('Controller: execute: %s(%s)', action_name, repr(params))
        result = action_method(**params)

        return result
