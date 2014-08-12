# -*- coding: utf-8 -*-

import pika
from logger import Logger


class AmqpListen:

    def __init__(self,
                 host,
                 user,
                 password,
                 virtual_host,
                 queue,
                 callback,
                 port=5672,
                 durable=True,
                 auto_delete=True,
                 no_ack=True,
                 timeout=5):

        self.logger = Logger.get_logger()

        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.virtual_host = virtual_host
        self.queue = queue
        self.callback = callback

        self.durable = durable
        self.auto_delete = auto_delete

        self.no_ack = no_ack

        self.listen()

    def listen(self):
        self.logger.debug('AmqpListen: start listen:\n'
                          '  host: %s\n'
                          '  port: %s\n'
                          '  VH: %s\n'
                          '  queue: %s\n'
                          '  user: %s\n'
                          '  pass: %s', self.host, self.port, self.virtual_host, self.queue, self.user, self.password)

        credentials = pika.PlainCredentials(self.user, self.password)
        connect_params = pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials)

        connection = pika.BlockingConnection(connect_params)
        channel = connection.channel()

        try:
            channel.queue_declare(queue=self.queue, passive=True)
        except pika.exceptions.ChannelClosed:
            self.logger.debug('AmqpListen: queue is not create. Process to create her.')
            channel = connection.channel()
            channel.queue_declare(queue=self.queue, durable=self.durable, auto_delete=self.auto_delete)

        channel.basic_consume(self.callback, queue=self.queue, no_ack=self.no_ack)
        channel.start_consuming()
