# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty


class MessageInterface:
    __metaclass__ = ABCMeta

    @abstractproperty
    def controller(self):
        """
        :rtype: C{str}
        """

    @abstractproperty
    def action(self):
        """
        :rtype: C{str}
        """

    @abstractproperty
    def params(self):
        """
        :rtype: dictionary
        """

    @abstractmethod
    def __repr__(self):
        pass