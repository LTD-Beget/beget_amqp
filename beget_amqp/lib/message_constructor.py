# -*- coding: utf-8 -*-

import json
from .message.message_to_service import MessageToService
from .message.message_amqp import MessageAmqp


class MessageConstructor:
    def __init__(self):
        pass

    @classmethod
    def create_message_amqp(cls, properties, body):
        dict_params = json.loads(body)
        controller = dict_params.get('controller', None)
        action = dict_params.get('action', None)
        params = dict_params.get('params', None)
        dependence = cls._get_dependence(properties)

        return MessageAmqp(controller, action, params, dependence=dependence)

    @classmethod
    def create_message_to_service(cls, body):
        dict_params = json.loads(body)
        controller = dict_params.get('controller', None)
        action = dict_params.get('action', None)
        params = dict_params.get('params', None)

        return MessageToService(controller, action, params)

    @classmethod
    def create_message_to_service_by_message_amqp(cls, message):
        return MessageToService(message.controller,
                                message.action,
                                message.params,
                                message.success_callback,
                                message.failure_callback)

    @classmethod
    def _get_dependence(cls, properties):
        headers = properties.headers
        if not isinstance(headers, dict):
            return None
        return headers.get('dependence')
