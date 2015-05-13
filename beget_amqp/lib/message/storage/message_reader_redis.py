# -*- coding: utf-8 -*-
from .storage_redis import StorageRedis


class MessageReaderRedis(StorageRedis):

    def get_message_by_uid(self, uid):
        key_list = self.redis.keys(self.MESSAGE_PREFIX + ':*:' + uid)

        if not key_list:
            return None

        return self.redis.hgetall(key_list[0])

    def get_all_message(self, queue=None):
        if not queue:
            queue = ''

        key_list = self.redis.keys(self.MESSAGE_PREFIX + ':' + queue + '*')

        msg_list = {}
        for key in key_list:
            msg_list[key] = self.redis.hgetall(key)

        return msg_list
