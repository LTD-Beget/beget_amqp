# -*- coding: utf-8 -*-

import traceback

from .logger import Logger


class Argument:

    def __init__(self):
        pass

    @staticmethod
    def check_type(check_value, need_type, default_value, strict_type=None):
        """
        Проверяем тип переменной. Если тип не корректный, возвращаем default значение.

        :param check_value: - проверяемая переменная

        :param need_type:  - желаемый тип проверяемой переменной
        :type need_type: tuple|type

        :param default_value:  - значение по умолчанию, если проверяемая переменная некорректна

        :param strict_type: - жесткая проверка типов. на DEV приводит к assert, на Prod пишет в лог.
        :type strict_type: tuple|type
        """
        assert isinstance(need_type, (tuple, type))

        # Жесткая проверка типа:
        if strict_type:
            # strict_type проверяем, если он есть
            assert isinstance(strict_type, (tuple, type))

            if not isinstance(check_value, strict_type):
                Logger.critical('Value: %s  have bad type: %s  Allow type: %s. \n  stack: %s',
                                repr(check_value),
                                type(check_value),
                                repr(strict_type),
                                ''.join(traceback.format_stack(limit=5)))

        # Обычная проверка типа:
        if isinstance(check_value, need_type):
            return check_value
        else:
            return default_value

    @staticmethod
    def have_method(obj, method_name):
        """
        Проверяем, есть ли в переданном объекте метод.
        :rtype : bool
        """
        if not hasattr(obj, method_name):
            return False
        if not callable(getattr(obj, method_name)):
            return False

        return True
