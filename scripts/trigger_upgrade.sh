#!/bin/sh

echo "Trigger upgrade in 10 seconds"
sleep 10
python mq_pub_15.py -i $1
