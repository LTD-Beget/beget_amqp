# -*- coding: utf-8 -*-


class CallbackData(Exception):
    """
    Класс исключение, для передачи кастомных данных в callback
    """
    def __init__(self, callback_key, data):
        """
        :param data: - данные передающиеся в callback. Используется ассоциативный массив, где ключ - это имя аргумента.
        :type data: dict

        :param callback_key: - имя каллбэка который должен быть вызван
        :type callback_key: basestring
        """
        assert isinstance(callback_key, basestring), 'callback_key must be a string, but is: %s' % repr(callback_key)
        assert isinstance(data, dict), 'data must be a dict, but is: %s' % repr(data)

        Exception.__init__(self)
        self.data = data
        self.callback_key = callback_key
