#!/usr/bin/env python
# -*- coding: utf-8 -*-

from beget_amqp import Sender
import examples.config as conf

print("""
DEBUG:
    amqp_user={},
    amqp_pass={},
    amqp_host={},
    amqp_port={},
    amqp_vhost={}
""".format(
    conf.AMQP_USER, conf.AMQP_PASS, conf.AMQP_HOST, conf.AMQP_PORT, conf.AMQP_VHOST
))


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


sender.send_low_level(conf.AMQP_QUEUE, get_body(10, '(1) RUN {1} [one, two] Две первые зависимости'),
                      properties=get_property(['one', 'two']))

sender.send_low_level(conf.AMQP_QUEUE, get_body(3, '(2) RUN {2} [one] Совместно выполняемая-1'),
                      properties=get_property(['one']))

sender.send_low_level(conf.AMQP_QUEUE, get_body(3, '(3) RUN {2} [two] Совместно выполняемая-2'),
                      properties=get_property(['two']))

sender.send_low_level(conf.AMQP_QUEUE,
                      get_body(20, '(4) RUN {3} [one, two, bravo] Долгая зависимость после первых трех'),
                      properties=get_property(['one', 'two', 'bravo']))

sender.send_low_level(conf.AMQP_QUEUE, get_body(3, '(5) RUN {4} [bravo] Освобожденная после долгой'),
                      properties=get_property(['bravo']))

sender.send_low_level(conf.AMQP_QUEUE,
                      get_body(3, '(6) RUN {1} [foxtrot] Завершится первой, так как без конкурентной зависимости'),
                      properties=get_property(['foxtrot']))

sender.send_low_level(conf.AMQP_QUEUE, get_body(3, '(7) RUN {1} [] Завершится второй, так как без зависимостей'),
                      properties=get_property([]))
