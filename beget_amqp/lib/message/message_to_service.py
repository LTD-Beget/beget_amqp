# -*- coding: utf-8 -*-

import json
from message import Message
from message_interface import MessageInterface


class MessageToService(Message):
    """
    Сообщение передачи его в callback, handler
    """
    def __init__(self, controller, action, params=None, success_callback=None, failure_callback=None):
        Message.__init__(self, controller, action, params)
        self.success_callback = success_callback if isinstance(success_callback, Message) else {}
        self.failure_callback = failure_callback if isinstance(failure_callback, Message) else {}

    def __repr__(self):
        message = {
            "controller": self.controller,
            "action": self.action,
            "params": self.params,
            "onSuccess": self.success_callback.__dict__ if isinstance(self.success_callback, MessageInterface) else {},
            "onFailure": self.failure_callback.__dict__ if isinstance(self.failure_callback, MessageInterface) else {}
        }

        return json.dumps(message)


if __name__ == '__main__':
    from message_callback import MessageCallback

    msg = MessageToService('myController', 'myAction', {'arg1': '1', 'arg2': '2'})
    print msg

    on_success = MessageCallback('exchange', 'myQueue', 'myController', 'onSuccessAction')
    on_failure = MessageCallback('exchange', 'myQueue', 'myController', 'onFailureAction')

    msg = MessageToService(
        'myController',
        'myAction',
        success_callback=on_success,
        failure_callback=on_failure
    )
    print msg
