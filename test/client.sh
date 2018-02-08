#!/bin/sh

cd /home/ubuntu/docker_based_cloudlet/test

sh ./cleanup.sh
python ../cloudlet.py service -l