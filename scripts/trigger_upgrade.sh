#!/bin/sh

echo "Trigger upgrade in 10 seconds"
sleep 10
python3 mq_pub_15.py -i $1 -p $2
