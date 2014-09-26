#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.getcwd())

from beget_amqp import Sender
import examples.config as conf


sender = Sender(
    user=conf.AMQP_USER,
    password=conf.AMQP_PASS,
    host=conf.AMQP_HOST,
    port=conf.AMQP_PORT,
    vhost=conf.AMQP_VHOST
)


def get_body(sleep_time, name):
    msg = {
        'controller': 'test',
        'action': 'sleep',
        'params': {
            'sleep_time': sleep_time,
            'name': name
        }
    }

    return sender.dict_to_body(msg)


def get_property(dependence):
    return {
        'headers': {
            'dependence': dependence
        }
    }

sender.send_low_level(conf.AMQP_QUEUE, get_body(10, 'Две первые зависимости'), properties=get_property(['one', 'two']))

sender.send_low_level(conf.AMQP_QUEUE, get_body(2, 'Совместно выполняемая-1'), properties=get_property(['one']))
sender.send_low_level(conf.AMQP_QUEUE, get_body(2, 'Совместно выполняемая-2'), properties=get_property(['two']))

sender.send_low_level(conf.AMQP_QUEUE,
                      get_body(20, 'Долгая зависимость после первых трех'),
                      properties=get_property(['one', 'two', 'bravo']))

sender.send_low_level(conf.AMQP_QUEUE, get_body(2, 'Освобожденная после долгой'), properties=get_property(['bravo']))

sender.send_low_level(conf.AMQP_QUEUE,
                      get_body(2, 'Завершится первой, так как без конкурентной зависимости'),
                      properties=get_property(['foxtrot']))

sender.send_low_level(conf.AMQP_QUEUE,
                      get_body(2, 'Завершится второй, так как без зависимостей'),
                      properties=get_property([]))
