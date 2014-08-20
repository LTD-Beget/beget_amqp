# -*- coding: utf-8 -*-

import pika
from logger import Logger


class AmqpListen:
    """
    Класс подключения к AMQP, прослушки очереди и передачи сообщений в указанную функцию
    """

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
                 no_ack=False,
                 prefetch_count=1):

        self.logger = Logger.get_logger()

        self.host = host
        self.user = user
        self.password = password
        self.virtual_host = virtual_host
        self.queue = queue
        self.callback = callback
        self.port = port

        self.durable = durable
        self.auto_delete = auto_delete
        self.no_ack = no_ack
        self.prefetch_count = prefetch_count

        # Обнуляем
        self.connection = None
        self.channel = None

    def start(self):
        """
        Начать прослушку и передачу сообщения в callback
        (При вызове, программа попадает в цикл. Выход рекомендован по сигналам)
        """
        self.logger.debug('AmqpListen: start listen:\n'
                          '  host: %s\n'
                          '  port: %s\n'
                          '  VH: %s\n'
                          '  queue: %s\n'
                          '  prefetch_count: %s\n'
                          '  user: %s\n'
                          '  pass: %s', self.host, self.port, self.virtual_host, self.queue, self.prefetch_count,
                          self.user, self.password)

        credentials = pika.PlainCredentials(self.user, self.password)
        connect_params = pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials)

        self.connection = pika.BlockingConnection(connect_params)
        self.channel = self.connection.channel()
        """:type : BlockingChannel"""

        try:
            self.channel.queue_declare(queue=self.queue, passive=True)
        except pika.exceptions.ChannelClosed:
            self.logger.debug('AmqpListen: queue is not create. Process to create her.')
            self.channel = self.connection.channel()
            """:type : BlockingChannel"""
            self.channel.queue_declare(queue=self.queue, durable=self.durable, auto_delete=self.auto_delete)

        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(self.callback, queue=self.queue, no_ack=self.no_ack)
        self.channel.start_consuming()

    def stop(self):
        """
        Завершить прослушивание
        """
        self.logger.debug('AmqpListen: stop listen')
        self.channel.stop_consuming()
