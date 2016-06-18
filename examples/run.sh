#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

>run.log

./run_with_debugging.py --workers=5 amqp-1 1>>run.log 2>&1 &

sleep 5

./send/message_for_test_dependence.py &

tail -f run.log
