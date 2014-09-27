#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, setproctitle
sys.path.insert(0, os.getcwd())

import beget_amqp
import examples.config as conf

import logging
logging.basicConfig(level=logging.CRITICAL)

beget_amqp_logger = beget_amqp.Logger.get_logger()
beget_amqp_logger.setLevel(level=beget_amqp.Logger.DEBUG)


from controllers_amqp import *
amqpControllerPrefix = 'controllers_amqp'

AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_VHOST,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix,
                                 number_workers=1,
                                 prefetch_count=1)

# Пример транспорта от beget_amqp с иным подключением.
transport = beget_amqp.get_transport(conf.AMQP_USER, conf.AMQP_PASS, conf.AMQP_HOST, int(conf.AMQP_PORT))
AmqpManager.add_transport(transport, 'amqp_test')
# Но при старте сервиса, в него уже добавляется стандартный транспорт по ключу 'amqp' с темеже данными подключения

try:
    import beget_msgpack

    # beget_msgpack_logger = beget_msgpack.Logger.get_logger('XXXXX')
    # beget_msgpack_logger.setLevel(logging.DEBUG)

    import examples.config_for_msgpack as config

    transport_msgpack = beget_msgpack.Transport(config)
    AmqpManager.add_transport(transport_msgpack, 'msgpack')
    print 'Have transport: beget_msgpack'
except Exception as e:
    print 'Haven\'t transport: beget_msgpack'

AmqpManager.start()
