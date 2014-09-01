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

    url = 'amqp://' + conf.AMQP_USER + ':' + conf.AMQP_PASS + '@' + conf.AMQP_HOST + ':' + conf.AMQP_PORT + '/' + conf.AMQP_EXCHANGE

    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 10, 'name': 'Две первые зависимости'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), ['one', 'two'])

    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 2, 'name': 'Совместно выполняемая-1'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), ['one'])
    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 2, 'name': 'Совместно выполняемая-2'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), ['two'])

    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 20, 'name': 'Долгая зависимость после первых трех'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), ['one', 'two', 'bravo'])

    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 2, 'name': 'Освобожденная после долгой'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), ['bravo'])

    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 2, 'name': 'Завершится первой, так как без конкурентной зависимости'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), ['foxtrot'])

    msg = {'controller': 'test', 'action': 'sleep', 'params': {'sleep_time': 2, 'name': 'Завершится второй, так как без зависимостей'}}
    Sender.send(url, conf.AMQP_QUEUE, json.dumps(msg), [])

    print 'send'