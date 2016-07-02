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


for i in range(30):
    sender.send_low_level(
        conf.AMQP_QUEUE,
        get_body(
            3,
            '({0}) RUN [bravo] Message number {0}'.format(i)
        ),
        properties=get_property(['bravo'])
    )
