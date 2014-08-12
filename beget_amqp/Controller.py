from .lib.logger import Logger


class Controller(object):
    def __init__(self, action_name):
        self.action_name = action_name
        self.logger = Logger.get_logger()

    def run_action(self, params):
        action_name = "action_%s" % str(self.action_name)
        action_method = getattr(self, action_name)

        self.logger.info('Exec: %s.%s(%s)', self.__class__.__name__, action_name, repr(params))
        result = action_method(**params)

        return result
