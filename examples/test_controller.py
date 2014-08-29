#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, setproctitle
sys.path.insert(0, os.getcwd())

# process_title = setproctitle.getproctitle()
# process_title += '_main_process'
# setproctitle.setproctitle(process_title)

import beget_amqp
import logging

logging.basicConfig(level=logging.CRITICAL)

logger = logging.getLogger('custom_name')
# or -> logger = beget_amqp.Logger.get_logger()  # Получить логгер с именем указанным для пакета.
logger.setLevel(logging.DEBUG)

#Пример клиентского контроллера (все они должны быть импортированы и находиться в определенной директории)
#Импортированные контроллеры должны быть доступны по prefix_name.controller_name
from controllers_amqp import *

import examples.config_for_test as conf


# import multiprocessing
# logger = multiprocessing.get_logger()
# logger = multiprocessing.log_to_stderr(1)


amqpControllerPrefix = 'controllers_amqp'
AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_EXCHANGE,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix,
                                 number_workers=5,
                                 logger_name='custom_name',
                                 service_name='MyService',
                                 prefetch_count=1)
AmqpManager.start()
