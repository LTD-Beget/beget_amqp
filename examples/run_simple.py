#!/usr/bin/env python
# -*- coding: utf-8 -*-

import beget_amqp
import config as conf

from controllers_amqp import *
amqpControllerPrefix = 'controllers_amqp'

AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_VHOST,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix)
AmqpManager.start()