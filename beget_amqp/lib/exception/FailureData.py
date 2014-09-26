# -*- coding: utf-8 -*-

from ...Callbacker import Callbacker
from .CallbackData import CallbackData


class FailureData(CallbackData):
    """
    Класс исключение, для передачи данных в failure callback
    """

    def __init__(self, data):
        """
        :type data: dict
        """
        CallbackData.__init__(self, Callbacker.EVENT_FAILURE, data)
