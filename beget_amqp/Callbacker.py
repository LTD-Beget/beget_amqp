# -*- coding: utf-8 -*-

from .lib.helpers.argument import Argument
from .lib.message.message_to_package import MessageToPackage
from .lib.helpers.logger import Logger
from .Sender import Sender


class Callbacker:
    """
    Задачи класса:
      - отправлять callback
    """

    # Имена событий:
    EVENT_SUCCESS = 'onSuccess'
    EVENT_FAILURE = 'onFailure'

    def __init__(self):
        pass

    @classmethod
    def send(cls, sender, event, message_to_package, params=None):
        """
        :param sender: объект отправителя, который может содержаться в себе доп.транспорты
        :type sender: beget_amqp.Sender.Sender

        :param event: Имя события
        :type event: basestring

        :param message_to_package: сообщение, которое может содержать в себе список и параметры callback
        :type message_to_package: beget_amqp.lib.message.message_to_package.MessageToPackage

        :param params: аргументы которые будут переданны в экшен
        :type params: dict
        """
        logger = Logger.get_logger()
        logger.debug('Callbacker: call event:%s', event)

        assert isinstance(event, basestring), 'event must be a string, but is: %s' % repr(event)
        assert isinstance(message_to_package, MessageToPackage), \
            'message_to_package must be MessageToPackage, but is: %s' % repr(message_to_package)

        callback_property = message_to_package.callback_list.get(event)

        if not callback_property:
            logger.debug('Callbacker: not have event: %s  in callback list: %s',
                         event, repr(message_to_package.callback_list))
            return False

        transport_name = callback_property.get('transport')
        path = callback_property.get('path')
        data_callback = callback_property.get('data', None)

        if not isinstance(params, dict) and data_callback is None:
            return False

        if not (transport_name and path):
            logger.debug('Callbacker: not found required param in callback: %s', repr(callback_property))
            return False

        # Sender может быть не указан при старте сервиса
        if not isinstance(sender, Sender):
            logger.debug('Callbacker: sender is not specified')
            return False

        transport = sender.get_transport(transport_name)
        if not transport:
            logger.debug('Callbacker: not found registered transport:%s', transport_name)
            return False

        logger.debug('Callbacker: send by:\n  transport:%s\n  path:%s\n  params:%s', transport_name, path, repr(params))

        params = Argument.check_type(params, dict, {}, strict_type=(type(None), dict))

        # Если в callback передавали данные то отправляется {key_from_callback_data: data, result: {dict_from_result}}
        if type(data_callback) is dict:
            if event != Callbacker.EVENT_FAILURE:
                params['result'] = params.copy()
            params.update(data_callback)

        transport.send(path, params)
