# -*- coding: utf-8 -*-

from ..helpers.argument import Argument


class ExceptionAction(Exception):
    """
    Исключение произошедшее в Action
    """

    def __init__(self, message, code=1, trace=None):
        """
        :type message: basestring
        :type code: int
        :type trace: basestring
        """
        self.message = Argument.check_type(message, basestring, 'No message', strict_type=basestring)
        self.code = Argument.check_type(code, int, 1, strict_type=int)
        self.trace = Argument.check_type(trace, basestring, '', strict_type=(type(None), basestring))

        Exception.__init__(self, self.message, self.code, self.trace)
