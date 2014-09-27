#!/usr/bin/env python
# -*- coding: utf-8 -*-

import beget_amqp


# Пример клиентского обработчика
class MyHandler():
    def __init__(self):
        print 'init handler'

    # обработчик должен содержать метод on_message
    def on_message(self, msg):
        print '\nmessage from handler: %s' % repr(msg)


if __name__ == "__main__":

    import config as conf

    AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                     conf.AMQP_USER,
                                     conf.AMQP_PASS,
                                     conf.AMQP_VHOST,
                                     conf.AMQP_QUEUE,
                                     handler=MyHandler)
    AmqpManager.start()
