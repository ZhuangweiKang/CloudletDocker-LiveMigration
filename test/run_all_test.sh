#!/bin/sh

cd /home/ubuntu/docker_based_cloudlet/test

echo "------------------------------------------------------------------"
echo "Clean up all containers and images ..."
sh ./cleanup.sh

echo "------------------------------------------------------------------"
echo "Running Test Case 1..."
sh ./normal-test/t1-server.sh

echo "------------------------------------------------------------------"
echo "Running Test Case 2..."
sh ./normal-test/t2-server.sh
