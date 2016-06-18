#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

>run3.log

./run_with_debugging.py --workers=2 amqp-1 1>>run3.log 2>&1 &
./run_with_debugging.py --workers=2 amqp-2 1>>run3.log 2>&1 &
./run_with_debugging.py --workers=2 amqp-3 1>>run3.log 2>&1 &

sleep 5

./send/message_for_test_dependence.py &

tail -f run3.log
