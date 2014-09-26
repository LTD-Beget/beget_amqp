#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.getcwd())

from beget_amqp.Sender import Sender
import examples.config as conf

# transport = 'amqp'
# path = 'sul_server/my_queue/test/'

transport = 'msgpack'

#server/controller/action
path = 'kon_server/test/'


class Message:
    get_error = {
        'controller': 'test',
        'action': 'error',
        'callbackList': {
            'onFailure': {
                # Если vhost указан в подключение и отправка в него же, то vhost можно не указывать:
                # 'path': 'my_queue/test/read_error_callback',
                # В ином случае следует его указать:
                # 'path': 'sul_server/my_queue/test/read_error_callback',

                'path': path + 'read_error_callback',
                'transport': transport
            },
        }
    }

    get_success = {
        'controller': 'test',
        'action': 'callback',
        'params': {
            'text': 'myText'
        },
        'callbackList': {
            'onSuccess': {
                'path': path + 'read_success_callback',
                'transport': transport
            },
        }
    }

    get_error_with_custom_data = {
        'controller': 'test',
        'action': 'error_with_custom_data',
        'callbackList': {
            'onFailure': {
                'path': path + 'read_error_with_custom_data',
                'transport': transport
            },
        }
    }

sender = Sender(
    user=conf.AMQP_USER,
    password=conf.AMQP_PASS,
    host=conf.AMQP_HOST,
    port=conf.AMQP_PORT,
    vhost=conf.AMQP_VHOST
)

print Message.get_error
body = sender.dict_to_body(Message.get_error_with_custom_data)

sender.send_low_level(
    conf.AMQP_QUEUE,
    body,
)
