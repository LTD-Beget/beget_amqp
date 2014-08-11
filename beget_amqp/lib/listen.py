# -*- coding: utf-8 -*-

import pika
import logging


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
                 no_ack=True):

        # logging.basicConfig(level=logging.CRITICAL)  # TODO: Delete this from code
        self.logger = logging.getLogger()

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
        self.logger.debug('AmqpListen: start listen: \n'
                          'host: %s\n' % self.host +
                          'port: %s\n' % self.port +
                          'VH: %s\n' % self.virtual_host +
                          'queue: %s' % self.queue)

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


if __name__ == '__main__':

    def my_callback(ch, method, properties, body):
        print """
        === get message
        chanel: %s
        detail chanel: %s
        method: %s
        detail method: %s
        properties: %s
        detail properties: %s
        body:%s'
        """ % (ch, ch.__dict__, method, method.__dict__, properties, properties.__dict__, body)

    import config_for_test as conf

    amqpSend = AmqpListen(conf.AMQP_HOST,
                          conf.AMQP_USER,
                          conf.AMQP_PASS,
                          conf.AMQP_EXCHANGE,
                          conf.AMQP_QUEUE,
                          my_callback)