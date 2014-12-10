# -*- coding: utf-8 -*-
import pika
from pika.exceptions import ChannelClosed

import json
import uuid

from .lib.helpers.argument import Argument
from .lib.helpers.logger import Logger


class Sender:

    # Имя транспорта
    TRANSPORT_MSGPACK = 'msgpack'
    TRANSPORT_AMQP = 'amqp'

    # Ожидаемый размер path
    _COUNT_WITH_VHOST = 4
    _COUNT_WITHOUT_VHOST = 3

    def __init__(self, user='guest', password='guest', host='localhost', port=5672, vhost=None):
        """
        Указать данные подключения
        Задача:
          - хранить информацию о данных подключения
        """
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.vhost = vhost

        self.logger = Logger.get_logger()

        self.transport_container = {
            # 'transport_name': transport_object
            self.TRANSPORT_AMQP: self
        }

    def send(self, path, params=None):
        """
        Отправка данных через amqp с использованием path строки.
        Задачи:
          - Класс может быть представлен в качестве транспорта @see Транспорт в README

        :param path: Строка указывающая путь отправки. Пример:
            - 'vhost/queue/controller/action'
            - 'queue/controller/action'  # используется vhost указанный в self.vhost
        :type path: str|unicode

        :param params: Передаваемые в action атрибуты
        :type params: dict|None
        """
        vhost, queue, controller, action = self._parse_path(path)
        self.send_by_args(queue, controller, action, params=params, vhost=vhost)

    def send_by_args(self, queue, controller, action, params=None, dependence=None, vhost=None):
        """
        Подготавливает стандартный формат сообщения и отправляет сообещение
        """
        message = {
            'controller': controller,
            'action': action,
            'params': params or {}
        }
        body = self.dict_to_body(message)

        properties = {
            'message_id': str(uuid.uuid4())
        }

        if dependence:
            dependence = Argument.check_type(dependence, list, [], strict_type=list)
            properties['headers'] = {'dependence': dependence}

        self.send_low_level(queue, body, properties, vhost)

    def send_low_level(self, queue, body, properties=None, vhost=None):
        """
        Предоставляет отправку с полным контролем тела письма

        :type queue: basestring
        :type vhost: basestring

        :param body: тело письма.
        :type body: basestring

        :param properties: параметры сообщения. Это message_id, header['dependence'] и т.д.
        :type properties: dict
        """
        vhost = vhost or self.vhost
        assert isinstance(vhost, basestring), 'vhost must be a string, but is: %s' % repr(vhost)
        assert isinstance(queue, basestring), 'queue must be a string, but is: %s' % repr(queue)
        assert isinstance(body, basestring), 'body must be a string, but is: %s' % repr(body)
        properties = Argument.check_type(properties, dict, {}, strict_type=(type(None), dict))

        self.logger.debug(
            'Sender: send message with:\n  vhost:%s\n  queue:%s\n  body:%s  \nproperties:%s',
            vhost, queue, body, properties
        )

        connection = self._get_amqp_connection(vhost)
        channel = self._get_amqp_channel(connection, queue)

        properties = pika.BasicProperties(**properties)
        channel.basic_publish('', queue, body, properties)
        connection.close()

    @staticmethod
    def dict_to_body(body):
        return json.dumps(body)

    ##########################
    # Работа с транспортом:

    def get_transport(self, transport_name=None):
        """
        Получить объект транспорта по его имени.
          - Если транспорт не указан, то возвращает стандартный AMQP транспорт.
          - Если транспорт указан но его нет, то возвращаем None
        :type transport_name: basestring|none
        :rtype : Sender|object|NoneType
        """
        if transport_name is None:
            return self.transport_container[Sender.TRANSPORT_AMQP]

        if transport_name in self.transport_container:
            return self.transport_container[transport_name]

        return None

    def add_transport(self, transport, transport_name):
        """
        Добавление транспорта, который может использовать Sender.
        :param transport: Объект транспорта, который содержит метод send
        :type transport: object
        :param transport_name: Имя-ключ транспорта, по которому мы получаем его
        :type transport_name: basestring
        """
        if not Argument.have_method(transport, 'send'):
            self.logger.error('Sender: transport has not method "send": %s', repr(transport))
            return False

        if not isinstance(transport_name, basestring):
            self.logger.error('Sender: transport_name must be a string: %s', repr(transport_name))
            return False

        self.transport_container[transport_name] = transport

    ##########################
    # Приватные методы:

    @staticmethod
    def _get_amqp_channel(connection, queue):
        channel = connection.channel()

        try:
            channel.queue_declare(queue=queue, passive=True)
        except pika.exceptions.ChannelClosed:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True, auto_delete=True)

        return channel

    def _get_amqp_connection(self, virtual_host):
        auth = pika.PlainCredentials(str(virtual_host), str(self.password))
        connect_params = pika.ConnectionParameters(host=str(self.host),
                                                   port=int(self.port),
                                                   virtual_host=str(virtual_host),
                                                   credentials=auth)

        return pika.BlockingConnection(connect_params)

    def _parse_path(self, path):
        """
        :param path: 'vhost/queue/controller/action' или 'queue/controller/action'
        :type path: str|unicode
        :rtype : tuple
        """
        path_split = path.split('/')

        if len(path_split) == self._COUNT_WITH_VHOST:
            return path_split
        elif (len(path_split) == self._COUNT_WITHOUT_VHOST) and self.vhost:

            # this return (vhost, queue, controller, action). If you know better syntax, let me know.
            return (self.vhost,) + tuple(path_split)
        else:
            raise Exception('String with bad format: %s\n But we expect: "vhost/queue/controller/action"' % repr(path))
