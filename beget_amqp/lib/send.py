# -*- coding: utf-8 -*-

import traceback
import pika
from logger import Logger

# TODO реализовать с зависимостями


class AmqpSend:

    def __init__(self, host, user, password, virtual_host, queue, data=None, port=5672, ext_params=None):
        self.logger = Logger.get_logger()
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.virtual_host = virtual_host
        self.queue = queue
        self.data = data
        self.ext_params = ext_params

    def send(self, data=None):
        self.logger.debug('AmqpSend: message to send:'
                          '  host: %s'
                          '  port: %s'
                          '  virtual host: %s'
                          '  queue: %s'
                          '  user: %s'
                          '  pass: %s'
                          '  data for send: %s', self.host, self.port, self.virtual_host, self.queue, self.user, self.password, data)

        credentials = pika.PlainCredentials(self.user, self.password)
        connect_params = pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials)

        try:
            connection = pika.BlockingConnection(connect_params)
            channel = connection.channel()
        except Exception as e:
            self.logger.error('AmqpSend: Exception: %s'
                              '  %s', e.message, traceback.format_exc())
            return False

        try:
            try:
                channel.queue_declare(queue=self.queue, passive=True)
            except pika.exceptions.ChannelClosed:
                channel = connection.channel()
                channel.queue_declare(queue=self.queue, durable=True, auto_delete=True)

            channel.basic_publish('', self.queue, data)
            connection.close()
            self.logger.info('AmqpSend: success send message to virtual host: %s  queue: %s', self.virtual_host, self.queue)
            return True
        except Exception as e:
            self.logger.error('AmqpSend: Exception: %s'
                              '  %s', e.message, traceback.format_exc())
            connection.close()
            return False
