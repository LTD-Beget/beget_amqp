# -*- coding: utf-8 -*-

import json
from message_interface import MessageInterface


class Message(MessageInterface):

    controller = None
    action = None
    params = None

    def __init__(self, controller, action, params=None):
        self.controller = controller
        self.action = action
        self.params = params

    def __repr__(self):
        message = {
            "controller": self.controller,
            "action": self.action,
            "params": self.params,
        }

        return json.dumps(message)


if __name__ == '__main__':
    msg = Message('myController', 'myAction', {'arg1': '1', 'arg2': '2'})
    print msg

    msg = Message('myController', 'myAction')
    print msg