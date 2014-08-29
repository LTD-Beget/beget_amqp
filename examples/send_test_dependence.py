#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika
import json


class Sender:
    def __init__(self):
        pass

    @staticmethod
    def send(url, queue, data, dependencies):
        connection = pika.BlockingConnection(pika.URLParameters(url))
        channel = connection.channel()

        try:
            channel.queue_declare(queue=queue, passive=True)
        except pika.exceptions.ChannelClosed:
            print 'queue doesn\'t exist. Create new.'
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True, auto_delete=True)

        channel.basic_publish('', queue, data, pika.BasicProperties(delivery_mode=2, headers={'dependence': dependencies}))
        connection.close()

if __name__ == '__main__':
    import config_for_test as conf
    import random

    for i in range(1, 100):
        dependencies = []

        #рандомное количество раз
        num_dependence = random.randint(0, 10)
        for x in range(1, num_dependence):
            #Рандомные зависимости
            dependencies.append(str(random.randint(1, 9)))

        msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 1, 'name': i}}
        print 'Dependencies: %s' % repr(dependencies)
        Sender.send('amqp://' + conf.AMQP_USER +
                    ':' + conf.AMQP_PASS +
                    '@' + conf.AMQP_HOST +
                    ':' + conf.AMQP_PORT +
                    '/' + conf.AMQP_EXCHANGE, conf.AMQP_QUEUE, json.dumps(msg), dependencies)
    print 'send'