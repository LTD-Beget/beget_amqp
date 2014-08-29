# -*- coding: utf-8 -*-

import json
from .message.message_to_service import MessageToService
from .message.message_amqp import MessageAmqp


class MessageConstructor:
    """
    Разные форматы сообщений преобразовывает к единому виду.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_message_amqp(properties, body):
        """
        Стандартное сообщение из AMQP
        """
        dict_params = json.loads(body)
        controller = dict_params.get('controller', None)
        action = dict_params.get('action', None)
        params = dict_params.get('params', None)
        dependence = MessageConstructor._get_dependence(properties)
        message_id = MessageConstructor._get_message_id(properties)

        return MessageAmqp(controller, action, params, dependence=dependence, message_id=message_id)

    @staticmethod
    def create_message_to_service(body):
        """
        Сообщение для обработчиков, контроллеров
        """
        dict_params = json.loads(body)
        controller = dict_params.get('controller', None)
        action = dict_params.get('action', None)
        params = dict_params.get('params', None)

        return MessageToService(controller, action, params)

    @staticmethod
    def create_message_to_service_by_message_amqp(message):
        """
        :type message: MessageAmqp
        """
        return MessageToService(message.controller,
                                message.action,
                                message.params,
                                message.success_callback,
                                message.failure_callback)

    @staticmethod
    def _get_dependence(properties):
        """
        Получаем зависимости из свойств сообщения
        """
        headers = properties.headers
        if not isinstance(headers, dict):
            return None
        return headers.get('dependence')

    @staticmethod
    def _get_message_id(properties):
        """
        Получаем уникальный id сообщения
        """
        return properties.message_id
