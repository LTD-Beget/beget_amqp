#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

LOGFILE=run2.log

>$LOGFILE

for i in `seq 1 2`; do
    ./run_with_debugging.py --workers=3 amqp-$i 1>>$LOGFILE 2>&1 &
done

sleep 5

./send/message_for_test_dependence.py &

tail -f $LOGFILE
