# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import beget_amqp as Amqp
import time


class TestController(Amqp.Controller):

    def action_test(self, some_arg):
        msg = 'TestController get: ' + some_arg
        print msg
        time.sleep(10)
        return msg