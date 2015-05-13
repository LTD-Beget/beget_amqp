# -*- coding: utf-8 -*-
from .comunicate import Communicate
import uuid
import time
import json


class CommunicateClient(Communicate):
    """
    Для создания запроса к серверу
    """

    def get_answer(self, question, queue=None, service_id=None, timeout_sec=5):
        """
        :param question: команда запроса.
        :type question: str

        :param queue: имя очереди к сервисам которых мы обращаемся
        :type queue: str

        :param service_id: имя сервиса к которому обращаемся.
        :type service_id: str

        Если queue и service_id пустые, то обращаемся ко всем amqp сервисам
        Если заполнено и queue и service_id, то используется service_id как наиболее конкретное

        :type timeout_sec: int

        :return: { service_id: ответ, ... }
        """

        if not isinstance(question, basestring):
            raise Exception('Not allowed format question: ' + str(type(question)))

        uuid_question = str(uuid.uuid4())[:8]
        result = {}

        if service_id:
            service_list = [service_id]
        elif queue:
            service_list = self.get_service_list(queue=queue).keys()
        else:
            service_list = self.get_service_list().keys()

        timeout = self.get_timeout(timeout_sec)

        self.debug('id: %s  question: %s  service: %s', uuid_question, question, repr(service_list))

        for service in service_list:
            self.redis.hset(service, self.PREFIX_QUESTION + uuid_question, question)

        while timeout.next():

            for service in service_list:
                answer = self.redis.hget(self.PREFIX_ANSWER + uuid_question, service)
                if answer:
                    try:
                        result[service] = json.loads(answer)
                    except ValueError:
                        result[service] = answer

                    service_list.remove(service)

            if not service_list:
                return result

            time.sleep(0.1)

        return result

    def get_service_list(self, queue=None):
        """
        Возвращает массив всех сервисов или сервисов слушающих определенную очередь

        :param queue:
        :type queue: str

        :return: {'service_id': 'queue', ...}
        """

        service_list = self.redis.hgetall(self.KEY_SERVICE_LIST)

        if not queue:
            self.debug('return server list: %s', repr(service_list))

            return service_list

        result = {}

        for service, service_queue in service_list.items():
            if service_queue == queue:
                result[service] = service_queue

        self.debug('by queue: %s  return server list: %s', queue, repr(result))

        return result

    def get_timeout(self, seconds):
        """
        Таймаут с использованием yeild
        :param seconds:
        :return:
        """
        time_end = time.time() + seconds

        while True:
            yield time.time() < time_end

    def debug(self, msg, *args):
        self.logger.debug('Redis: AmqpCommunicateClient: ' + msg, *args)
