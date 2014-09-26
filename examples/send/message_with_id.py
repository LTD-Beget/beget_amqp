#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.getcwd())

import random
import uuid

from beget_amqp import Sender
import examples.config as conf

sender = Sender(
    user=conf.AMQP_USER,
    password=conf.AMQP_PASS,
    host=conf.AMQP_HOST,
    port=conf.AMQP_PORT,
    vhost=conf.AMQP_VHOST
)

msg = {
    'controller': 'test',
    'action': 'sleep',
    'params': {
        'sleep_time': 5,
        'name': 'message with id'
    }
}

body = sender.dict_to_body(msg)

properties = {
    # можно указать статичную строку и посмотреть, что второе сообщение будет отброшенно как дублирующее.
    'message_id': str(uuid.uuid4())
}

sender.send_low_level(
    conf.AMQP_QUEUE,
    body,
    properties=properties
)
