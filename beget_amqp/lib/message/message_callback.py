# -*- coding: utf-8 -*-
# Project server.pyportal

import json
from message import Message
from ..send import AmqpSend
from ..config import AMQP_PASS, AMQP_HOST, AMQP_USER  # todo этого не должно быть


class MessageCallback(Message):

    def __init__(self, virtual_host, queue, controller, action, params=None):
        Message.__init__(self, controller, action, params)
        self.queue = queue
        self.virtual_host = virtual_host

    def __call__(self, *args, **kwargs):
        params_buff = self.params

        if not self.virtual_host or not self.queue:
            raise Exception('Must specify virtual_host and queue')

        if args and not kwargs:
            if len(args) > 1:
                self.params = args
            else:
                self.params = args[0]
        elif kwargs and not args:
            self.params = kwargs
        elif args and kwargs:
            raise NotImplementedError("only args or kwargs")

        amqp_send = AmqpSend(AMQP_HOST, AMQP_USER, AMQP_PASS, self.virtual_host, self.queue)
        result = amqp_send.send(repr(self))
        self.params = params_buff
        return result

    def __repr__(self):
        message = {
            "virtual_host": self.virtual_host,
            "queue": self.queue,
            "controller": self.controller,
            "action": self.action,
            "params": self.params,
        }

        return json.dumps(message)
