#!/usr/bin/env python
# -*- coding: utf-8 -*-

import beget_amqp

#Пример клиентского контроллера (все они должны быть импортированы и находиться в определенной директории)

#Импортированные контроллеры должны быть доступны по prefix_name.controller_name
from controllers_amqp import *

import config_for_test as conf
amqpControllerPrefix = 'controllers_amqp'

AmqpManager = beget_amqp.Service(conf.AMQP_HOST,
                                 conf.AMQP_USER,
                                 conf.AMQP_PASS,
                                 conf.AMQP_EXCHANGE,
                                 conf.AMQP_QUEUE,
                                 controllers_prefix=amqpControllerPrefix)
AmqpManager.start()