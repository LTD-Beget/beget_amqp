#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.getcwd())

import random

from beget_amqp import Sender
import examples.config as conf


sender = Sender(
    user=conf.AMQP_USER,
    password=conf.AMQP_PASS,
    host=conf.AMQP_HOST,
    port=conf.AMQP_PORT,
    vhost=conf.AMQP_VHOST
)

for i in range(1, 100):

    dependencies = []
    for useless in range(1, random.randint(0, 10)):
        #Рандомное количество рандомных зависимостей
        dependencies.append(str(random.randint(1, 9)))

    print i, 'Dependencies: %s' % repr(dependencies)

    # Использование разных способов отправки:
    if random.getrandbits(1):
        # Через более высокий уровень, аргументы:
        sender.send_by_args(conf.AMQP_QUEUE,
                            controller='test',
                            action='sleep',
                            params={'sleep_time': 3, 'name': str(i) + '-up_level'},
                            dependence=dependencies)

    else:
        # Через кастомное создание письма и свойств:
        msg = {
            'controller': 'test',
            'action': 'sleep',
            'params': {
                'sleep_time': 3,
                'name': str(i) + '-low_level'
            }
        }
        body = sender.dict_to_body(msg)

        properties = {
            'headers': {
                'dependence': dependencies
            }
        }

        sender.send_low_level(
            conf.AMQP_QUEUE,
            body,
            properties=properties
        )
