# -*- coding: utf-8 -*-

import json
import platform
import uuid
from message_interface import MessageInterface
from message_to_service import MessageToService
from message_callback import MessageCallback


class MessageAmqp(MessageToService, MessageCallback):
    """
    Сообщение для обработки внутри модуля
    """
    VERSION = "1.0"

    def __init__(self,
                 controller,
                 action,
                 params=None,
                 success_callback=None,
                 failure_callback=None,
                 virtual_host=None,
                 queue=None,
                 dependence=None,
                 message_id=None):

        MessageToService.__init__(self, controller, action, params, success_callback, failure_callback)
        MessageCallback.__init__(self, virtual_host, queue, controller, action, params)
        self.hostname = platform.node()
        self.dependence = dependence
        self.id = message_id or str(uuid.uuid4())

    def __repr__(self):
        msg = {
            "version": self.VERSION,
            "from": self.hostname,
            "controller": self.controller,
            "action": self.action,
            "params": self.params,
            "vhost": self.virtual_host,
            "queue": self.queue,
            "onSuccess": self.success_callback.__dict__ if isinstance(self.success_callback, MessageInterface) else {},
            "onFailure": self.failure_callback.__dict__ if isinstance(self.failure_callback, MessageInterface) else {},
        }

        return json.dumps(msg)


if __name__ == '__main__':
    message = MessageAmqp('exchange', 'myQueue', 'myController', 'myAction')
    print message

    on_success = MessageCallback('exchange', 'myQueue', 'myController', 'onSuccessAction', {'answer': True})
    on_failure = MessageCallback('exchange', 'myQueue', 'myController', 'onFailureAction', {'debugParams': 'errorText'})
    message = MessageAmqp('myController',
                          'myAction',
                          {'arg1': '1', 'arg2': 2},
                          on_success,
                          on_failure,
                          'exchange',
                          'myQueue')
    print message
