import logging


class Controller(object):
    def __init__(self, action_name, logger=None):
        self.action_name = action_name
        self.logger = logger or logging.getLogger("dummy")

    def run_action(self, params):
        action_name = "action_%s" % str(self.action_name)
        action_method = getattr(self, action_name)

        result = action_method(**params)

        return result