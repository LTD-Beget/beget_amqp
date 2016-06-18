#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

>run2.log

./run_with_debugging.py --workers=3 amqp-1 1>>run2.log 2>&1 &
./run_with_debugging.py --workers=3 amqp-2 1>>run2.log 2>&1 &

sleep 5

./send/message_for_test_dependence.py &

tail -f run2.log
