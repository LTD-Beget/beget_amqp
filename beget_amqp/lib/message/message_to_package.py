# -*- coding: utf-8 -*-

import uuid
from ..helpers.argument import Argument


class MessageToPackage(object):
    """
    Сообщение для обработки внутри пакета.

    Задача:
      - Единожды получить данные из AMQP и иметь к ним контролируемый доступ
      - Обозначить обязательные и опциональные параметры AMQP сообщения. Все остальные параметры игнорировать.
    """

    def __init__(self,
                 controller,
                 action,
                 params=None,
                 dependence=None,
                 message_id=None,
                 callback_list=None,
                 expiration=None):
        """
        Сообщение обязано содержать:
            :type controller:basestring
            :type action:basestring

        Сообщение может содержать:
            :param params: Предназначены для вызываемого экшена.
            :type params: None|dict

            :param dependence: Устраняет конфликты при выполнение нескольких сообщений одновременно.
            :type dependence: None|list|dict

            :param message_id: Обеспечивает возможность различать сообщения
            :type message_id: None|basestring

            :param callback_list: Указывает 'Событие => данные для обратного вызоыва'
            :type callback_list: None|dict

            :param expiration: Указывает ttl сообщения в секундах.
            :type expiration: None|int
        """
        if type(dependence) is dict:
            dependence = dependence.values()
        
        assert isinstance(controller, basestring), 'controller must be a string, but is: %s' % repr(controller)
        self.controller = controller

        assert isinstance(action, basestring), 'action must be a string, but is: %s' % repr(action)
        self.action = action

        self.params = Argument.check_type(params, dict, {}, strict_type=(type(None), list, dict))
        self.dependence = Argument.check_type(dependence, list, [], strict_type=(type(None), list))
        self.expiration = Argument.check_type(expiration, int, 0)
        self.id = Argument.check_type(message_id, basestring, str(uuid.uuid4()), strict_type=(type(None), basestring))
        self.callback_list = Argument.check_type(callback_list, dict, {}, strict_type=(type(None), list, dict))
