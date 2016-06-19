#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, setproctitle
sys.path.insert(0, os.getcwd())

import beget_amqp
import logging

logging.basicConfig(level=logging.CRITICAL)

logger = logging.getLogger('custom_name')
# or -> logger = beget_amqp.Logger.get_logger()  # Получить логгер с именем указанным для пакета.
logger.setLevel(logging.DEBUG)

#Пример клиентского контроллера (все они должны быть импортированы и находиться в определенной директории)
#Импортированные контроллеры должны быть доступны по prefix_name.controller_name
from controllers_amqp import *

import examples.config as conf


# import multiprocessing
# logger = multiprocessing.get_logger()
# logger = multiprocessing.log_to_stderr(1)


amqpControllerPrefix = 'controllers_amqp'
AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_VHOST,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix,
                                 number_workers=10,
                                 logger_name='custom_name',
                                 prefetch_count=1)

transport = beget_amqp.get_transport(conf.AMQP_USER, conf.AMQP_PASS, conf.AMQP_HOST, int(conf.AMQP_PORT))
AmqpManager.add_transport(transport, 'amqp_test')

try:
    import beget_msgpack
    import examples.config_for_msgpack as config
    transport_msgpack = beget_msgpack.Transport(config)
    AmqpManager.add_transport(transport_msgpack, 'msgpack')
    print 'Have transport: beget_msgpack'
except Exception as e:
    print 'Haven\'t transport: beget_msgpack'

AmqpManager.start()
