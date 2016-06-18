#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import beget_amqp
import logging
import argparse

from controllers_amqp import *

import config as conf
amqpControllerPrefix = 'controllers_amqp'

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--workers', type=int, default=3, help="Number of workers")
parser.add_argument('name', help="Logger (or program) name")

args = parser.parse_args()

logger_name = args.name
number_workers = args.workers

# set level for another loggers:
logging.basicConfig(
    level=logging.CRITICAL,
    format='%(filename)-20s#%(lineno)-4d: %(name)s:%(levelname)-6s [%(asctime)s][%(process)d] %(message)s'
)

# set level for beget_amqp logger:
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

AmqpManager = beget_amqp.Service(
    conf.AMQP_HOST,
    conf.AMQP_USER,
    conf.AMQP_PASS,
    conf.AMQP_VHOST,
    conf.AMQP_QUEUE,
    controllers_prefix=amqpControllerPrefix,
    number_workers=number_workers,
    logger_name=logger_name
)

AmqpManager.start()