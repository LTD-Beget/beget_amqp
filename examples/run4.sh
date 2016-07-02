#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

LOGFILE=run4.log

>$LOGFILE

for i in `seq 1 4`; do
    ./run_with_debugging.py --workers=2 amqp-$i 1>>$LOGFILE 2>&1 &
done

sleep 5

./send/message_for_test_dependence.py &

tail -f run4.log
