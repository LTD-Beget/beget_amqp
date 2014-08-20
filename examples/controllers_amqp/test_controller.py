# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import beget_amqp as amqp
import time
import os


class TestController(amqp.Controller):

    def action_test(self, some_arg):
        print 'some_arg type:', type(some_arg)
        print 'some_arg repr:', repr(some_arg)

    def action_sleep(self, sleep_time, name=None):
        assert isinstance(sleep_time, (int, float)), 'sleep_time must be int or float'
        my_pid = os.getpid()
        my_name = name if name else my_pid
        print '%s:sleep: %s' % (my_name, str(sleep_time))
        time.sleep(sleep_time)
        print '%s:exit' % my_name

    def action_error(self):
        raise Exception('Standard error')

    def action_kill_me(self, sleep_time=None):
        print '===== kill me. pid:', os.getpid()
        sleep_time_final = sleep_time if isinstance(sleep_time, (int, float)) else 120
        for i in range(1, sleep_time_final):
            time.sleep(1)
            print i
        print 'exit from kill me'
