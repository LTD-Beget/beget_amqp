# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json


class MessageCallback(object):
    TYPE_AMQP = "amqp"
    TYPE_MSGPACK = "msgpack"

    EVENT_SUCCESS = "success"
    EVENT_FAILURE = "failure"

    def __init__(self):
        self.type = None
        self.event = None
        self.neededParams = {}

        self.controller = None
        self.action = None

        """
        @type Message
        """
        self.message = None

    def get_controller(self):
        return self.message.controller if self.controller is None else self.controller

    def get_action(self):
        if self.action is not None:
            return self.action

        if self.event == self.EVENT_FAILURE:
            return "%s_failure" % self.message.action
        elif self.event == self.EVENT_SUCCESS:
            return "%s_success" % self.message.action
        else:
            return None

    def __repr__(self):
        msg = {
            "type": self.type,
            "event": self.event,
            "neededParams": self.neededParams,
            "controller": self.get_controller(),
            "action": self.get_action()
        }

        return json.dumps(msg)