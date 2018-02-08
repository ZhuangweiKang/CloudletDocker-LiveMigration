#!/bin/sh

cd /home/ubuntu/docker_based_cloudlet/test

docker run -d --name t2 --security-opt seccomp:unconfined ubuntu \
    /bin/sh -c 'i=0; while true; do echo $i; i=$(expr $i + 1); sleep 1; done'

python ../cloudlet.py migrate t2 -t 129.59.107.141