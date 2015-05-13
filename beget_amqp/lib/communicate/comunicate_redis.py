# -*- coding: utf-8 -*-
import uuid
import json
from .comunicate import Communicate


class CommunicateRedis(Communicate):
    """
    Для получения запросов и ответа на них
    """

    def __init__(self, queue, socket="/var/run/redis/redis.sock"):
        super(CommunicateRedis, self).__init__(socket)

        self.queue = queue
        self.uid = str(uuid.uuid4())[:8]
        self.key = queue + '_' + self.uid
        self.register()

    def register(self):
        self.redis.hset(self.KEY_SERVICE_LIST, self.key, self.queue)

    def __del__(self):
        self.unregister()

    def unregister(self):
        self.redis.hdel(self.KEY_SERVICE_LIST, self.key)
        self.redis.delete(self.key)

    def get_question_list(self):
        question_list = {}

        for hash_key in self.redis.hkeys(self.key):
            if hash_key.startswith(self.PREFIX_QUESTION):
                question_hash = hash_key[len(self.PREFIX_QUESTION):]
                question_list[question_hash] = self.redis.hget(self.key, hash_key)

            self.redis.hdel(self.key, hash_key)

        return question_list

    def set_answer(self, hash_key, answer):
        if isinstance(answer, (list, dict, tuple, bool, type(None))):
            answer = json.dumps(answer)
        elif not isinstance(answer, basestring):
            answer = 'Bad format from answer method: ' + str(type(answer))
        self.debug('set answer: key:%s val:%s', self.PREFIX_ANSWER + hash_key, answer)

        # В отдельный ключ, чтобы использовать expired
        answer_key = self.PREFIX_ANSWER + hash_key
        self.redis.hset(answer_key, self.key, answer)
        self.redis.expire(answer_key, self.LOCAL_STORAGE_LIVE_TIME)

    def debug(self, msg, *args):
        self.logger.debug('Redis: ' + msg, *args)
