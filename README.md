Basic usage
============

    git clone https://github.com/LTD-Beget/beget_amqp

    cd beget_amqp/
    python setup.py install

    cd examples/
    vi config_for_test.py

    python send_message.py      # Send test message
    python test_controller.py   # Get test message


Alternative usage
============
Installation:

    pip install beget_amqp

Script for working with controllers:
```python
import beget_amqp as Amqp

# 'Service' - allows you to start listening AMQP
# controllers_prefix - specifies a prefix for controllers
# See the examples for understanding how to location controllers.
AmqpManager = Amqp.Service(conf.AMQP_HOST,
                           conf.AMQP_USER,
                           conf.AMQP_PASS,
                           conf.AMQP_EXCHANGE,
                           conf.AMQP_QUEUE,
                           controllers_prefix='controllers_amqp')
AmqpManager.start()
```

Script for working with custom handlers:
```python
import beget_amqp as Amqp

# handler must contain 'on_message' method. You can inherit Amqp.Handler
class MyHandler():
    def on_message(self, msg):
        print 'message from handler: %s' % repr(msg)

AmqpManager = Amqp.Service(conf.AMQP_HOST,
                           conf.AMQP_USER,
                           conf.AMQP_PASS,
                           conf.AMQP_EXCHANGE,
                           conf.AMQP_QUEUE,
                           handler=MyHandler)
AmqpManager.start()
```
