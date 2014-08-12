
import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing import Lock
import time
from ..logger import Logger


class DependenceSyncManager(object):
    def __init__(self):
        self.dict_of_queue = {}
        self.lock = Lock()
        self.logger = Logger.get_logger()

    #////////////////////////////////////////////////////////////////////////////
    def set_and_wait(self, message):
        self.set(message)
        self.wait(message)

    #////////////////////////////////////////////////////////////////////////////
    def wait(self, message):
        """
        infinity loop until I got permission to continue
        """
        self.logger.debug('DependenceSyncManager: wait-dependence: %s', repr(message.dependence))
        while True:
            if self.is_available_dependence(message):
                return True
            time.sleep(0.1)

    #////////////////////////////////////////////////////////////////////////////
    def is_available_dependence(self, message):
        """
        Check whether our turn
        """
        for dep in message.dependence:
            if dep in self.dict_of_queue:
                if message.id != self.dict_of_queue[dep][0]:  # compare our id with id first in queue
                    return False
        return True

    #////////////////////////////////////////////////////////////////////////////
    def set(self, message):
        """
        Set our dependencies in queue
        """
        self.logger.debug('DependenceSyncManager: set-dependence: %s', repr(message.dependence))
        self.lock.acquire()  # in one moment only one worker may write dependence. Otherwise we may get deadlock.
        for dep in message.dependence:
            if dep in self.dict_of_queue:
                self.dict_of_queue[dep].append(message.id)  # if we have queue by dependence name, we add id in queue
            else:
                self.dict_of_queue[dep] = [message.id]
        self.lock.release()

    #////////////////////////////////////////////////////////////////////////////
    def release(self, message):
        """
        Release our dependencies from queue
        """
        self.logger.debug('DependenceSyncManager: release-dependence: %s', repr(message.dependence))
        for dep in message.dependence:
            if dep in self.dict_of_queue:
                while message.id in self.dict_of_queue[dep]:
                    self.dict_of_queue[dep].remove(message.id)

    @staticmethod
    def get_manager():
        class CreatorSharedManager(BaseManager):
            pass

        CreatorSharedManager.register('DependenceSyncManager', DependenceSyncManager)
        creator_shared_manager = CreatorSharedManager()
        creator_shared_manager.start()
        return creator_shared_manager.DependenceSyncManager()  # it's create shared object between multiprocessing


################################################################################
# Testing

if __name__ == '__main__':

    import datetime
    from ..message.message_amqp import MessageAmqp

    class Worker(multiprocessing.Process):
        def __init__(self, dependence_manager, job):
            multiprocessing.Process.__init__(self)
            self.dependence_manager = dependence_manager
            self.job = job
            self._start = datetime.datetime.now()
            self._end = None

        def run(self):
            print '%s    id:%s secToWork: %s    dependence: %s' % (self.job.action,
                                                                   self.job.id,
                                                                   self.job.params['sec'],
                                                                   self.job.dependence)
            self.dependence_manager.set_and_wait(self.job)
            time.sleep(self.job.params['sec'])
            self.dependence_manager.release(self.job)
            self._end = datetime.datetime.now()
            result = self._end - self._start

            print '%s    id:%s completed in %s seconds' % (self.job.action, self.job.id, result.seconds)


    jobs = [
        MessageAmqp('myController', '1', {'sec': 30}, dependence=['site.ru', 'customer12345']),
        MessageAmqp('myController', '2', {'sec': 5}, dependence=['site.ru']),
        MessageAmqp('myController', '3', {'sec': 10}, dependence=['KeyOfBackup']),
        MessageAmqp('myController', '4', {'sec': 5}, dependence=['customer12345']),
        MessageAmqp('myController', '5', {'sec': 1}, dependence=['KeyOfBackup'])
    ]

    shared_manager = DependenceSyncManager.get_manager()

    workers = []
    for job in jobs:
        w = Worker(shared_manager, job)
        w.start()
        workers.append(w)
        time.sleep(0.1)
    print '-----'

    for worker in workers:
        worker.join()