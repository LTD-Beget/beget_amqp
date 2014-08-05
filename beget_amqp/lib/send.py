# -*- coding: utf-8 -*-

import pika
import logging


class AmqpSend:

    def __init__(self, host, user, password, virtual_host, queue, data=None, port=5672, ext_params=None):
        logging.basicConfig(level=logging.CRITICAL)  # TODO: Delete this from code
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.virtual_host = virtual_host
        self.queue = queue
        self.data = data
        self.ext_params = ext_params

    def send(self, data=None):
        credentials = pika.PlainCredentials(self.user, self.password)
        connect_params = pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials)

        try:
            connection = pika.BlockingConnection(connect_params)
            channel = connection.channel()
        except:
            return False

        try:
            try:
                channel.queue_declare(queue=self.queue, passive=True)
            except pika.exceptions.ChannelClosed:
                channel = connection.channel()
                channel.queue_declare(queue=self.queue, durable=True, auto_delete=True)

            channel.basic_publish('', self.queue, data)
            connection.close()
            return True
        except:
            connection.close()
            return False
