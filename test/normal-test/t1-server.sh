#!/bin/sh

cd /home/ubuntu/docker_based_cloudlet/test

docker run -d --name t1 --security-opt seccomp:unconfined busybox \
    /bin/sh -c 'i=0; while true; do echo $i; i=$(expr $i + 1); sleep 1; done'

python ../cloudlet.py migrate t1 -t 129.59.107.141