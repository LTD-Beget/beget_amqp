#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

LOGFILE=run_single25.log

>$LOGFILE

./run_with_debugging.py --workers=25 amqp-1 1>>$LOGFILE 2>&1 &

sleep 5

./send/message_for_test_single_dependence.py &

tail -f $LOGFILE
