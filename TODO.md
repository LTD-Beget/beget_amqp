# When killing SyncManager, we have 2 implications:
  - In /tmp/pymp-* we spawned file sockets
  - Worker slow stopping because try connect to manager.

Debug:
```
    [INFO/AmqpWorker-2(23299)] process shutting down
    [DEBUG/AmqpWorker-2(23299)] DECREF '24f1dd0'
    # here 5 seconds timeout
    [DEBUG/AmqpWorker-2(23299)] failed to connect to address /tmp/pymp-5x0zZy/listener-h6b1aj
    [DEBUG/AmqpWorker-2(23299)] ... decref failed [Errno 111] Connection refused
    [DEBUG/AmqpWorker-2(23299)] thread 'MainThread' has no more proxies so closing conn
    [DEBUG/AmqpWorker-2(23299)] running the remaining "atexit" finalizers
    [INFO/AmqpWorker-2(23299)] process exiting with exitcode 0
```

