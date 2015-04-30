# -*- coding: utf-8 -*-

import json
from .message.message_to_handler import MessageToHandler
from .message.message_to_package import MessageToPackage


class MessageConstructor:
    """
    Разные форматы сообщений преобразовывает к единому виду.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_message_amqp(body, properties):
        """
        Стандартное сообщение из AMQP
        """
        body_params = json.loads(body)

        # Обязательные данные
        controller = body_params['controller']
        action = body_params['action']

        # Опциональные данные
        params = body_params.get('params', {})
        callback_list = body_params.get('callbackList')

        message_id = properties.message_id
        """:type message_id: None|basestring"""

        headers = properties.headers
        """:type headers: None|dict"""

        if not isinstance(headers, dict):
            headers = {}

        dependence = headers.get('dependence', [])
        expiration = headers.get('expiration', 0)

        return MessageToPackage(controller,
                                action,
                                params,
                                dependence=dependence,
                                message_id=message_id,
                                callback_list=callback_list,
                                expiration=expiration)

    @staticmethod
    def create_message_to_service_by_message_amqp(message):
        return MessageToHandler(message.controller, message.action, message.params)
