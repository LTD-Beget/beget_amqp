# -*- coding: utf-8 -*-
import uuid

from .Controller import Controller
from .Handler import Handler
from .Service import Service
from .lib.helpers.logger import Logger
from .Sender import Sender

# Исключение, которое предлагается использовать для передачи сообщения об ошибки в callback
from .lib.exception.ExceptionAction import ExceptionAction
from .lib.exception.ExceptionHandler import ExceptionHandler

# Исключения, для передачи данных в callback:
from .lib.exception.CallbackData import CallbackData
from .lib.exception.FailureData import FailureData

from ._version import __version__


# Получение транспорта их пакета
def get_transport(user='guest', password='guest', host='localhost', port=5672, vhost=None):
    sender = Sender(user, password, host, port, vhost)
    return sender.get_transport()


def get_lockfile(name):
    return '/var/run/beget_amqp.{}.lock'.format(name)


def generate_uuid():
    return str(uuid.uuid4())
