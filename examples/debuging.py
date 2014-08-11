#!/usr/bin/env python
# -*- coding: utf-8 -*-

import beget_amqp
import logging

from controllers_amqp import *

import config_for_test as conf
amqpControllerPrefix = 'controllers_amqp'

# set level for another loggers:
logging.basicConfig(level=logging.CRITICAL)

# set level for beget_amqp logger:
beget_amqp_logger = logging.getLogger('beget_amqp')
beget_amqp_logger.setLevel(logging.DEBUG)

AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_EXCHANGE,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix)
AmqpManager.start()