# -*- coding: utf-8 -*-

from multiprocessing import Process
from .message_constructor import MessageConstructor
from .listen import AmqpListen
import signal
import os
import sys
import logging

class AmqpWorker(Process):

    STATUS_START = 1
    STATUS_STOP = 0

    def __init__(self,
                 host,
                 user,
                 password,
                 virtual_host,
                 queue,
                 callback,
                 dependence_sync_manager,
                 port=5672,
                 id=None,
                 durable=True,
                 auto_delete=False,
                 no_ack=True):

        Process.__init__(self)

        self.logger = logging.getLogger()
        self.host = host
        self.user = user
        self.password = password
        self.virtual_host = virtual_host
        self.port = port
        self.queue = queue
        self.callback = callback

        self.durable = durable
        self.auto_delete = auto_delete
        self.no_ack = no_ack

        self.dependence_sync_manager = dependence_sync_manager
        self.id = str(id) if id else "None"

    def sig_handler(self, signal, frame):
        self.logger.debug('killing worker with pid: %s', os.getpid())
        self.stop()
        sys.exit(1)

    #////////////////////////////////////////////////////////////////////////////
    def run(self):
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        amqp_listen = AmqpListen(self.host,
                                 self.user,
                                 self.password,
                                 self.virtual_host,
                                 self.queue,
                                 self._on_message,
                                 self.port,
                                 self.durable,
                                 self.auto_delete,
                                 self.no_ack)

    #////////////////////////////////////////////////////////////////////////////
    def _on_message(self, ch, method, properties, body):
        self.logger.debug('get message properties: %s   body: %s', properties, body)
        message_constructor = MessageConstructor()
        message_amqp = message_constructor.create_message_amqp(properties, body)
        self.set_dependence(message_amqp)
        message_to_service = message_constructor.create_message_to_service_by_message_amqp(message_amqp)
        self.wait_dependence(message_amqp)
        try:
            self.callback(message_to_service)
        except Exception as e:
            pass
        self.release_dependence(message_amqp)

    #////////////////////////////////////////////////////////////////////////////
    def set_dependence(self, message_amqp):
        if message_amqp.dependence:
            self.dependence_sync_manager.set(message_amqp)

    #////////////////////////////////////////////////////////////////////////////
    def wait_dependence(self, message_amqp):
        if message_amqp.dependence:
            self.dependence_sync_manager.wait(message_amqp)

    #////////////////////////////////////////////////////////////////////////////
    def release_dependence(self, message_amqp):
        if message_amqp.dependence:
            self.dependence_sync_manager.release(message_amqp)

    def stop(self):
        self.logger.debug('stop worker')
