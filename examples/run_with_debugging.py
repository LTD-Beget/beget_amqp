#!/usr/bin/env python
# -*- coding: utf-8 -*-

import beget_amqp
import logging

from controllers_amqp import *

import config as conf
amqpControllerPrefix = 'controllers_amqp'

# set level for another loggers:
logging.basicConfig(level=logging.CRITICAL)

# set level for beget_amqp logger:
beget_amqp_logger = beget_amqp.Logger.get_logger('xxx')
beget_amqp_logger.setLevel(logging.DEBUG)

AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_VHOST,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix,
                                 number_workers=1)
AmqpManager.start()