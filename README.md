#[Test Environment]:

python 2.7

ubuntu 16.04

Linux Kernel: 4.14.0-041400-generic

criu 3.7

#[Dependency]:
dependency.sh

#[How to use]:

!need root privilege now

        python cloudlet.py [argv]
        example:
        
        VM1:
        
        $python cloudlet.py check
        $ docker run -d --name looper2 --security-opt seccomp:unconfined busybox \
        /bin/sh -c 'i=0; while true; do echo $i; i=$(expr $i + 1); sleep 1; done'
        $python cloudlet.py migrate looper2 -t 192.168.x.x(ip of vm2)
        
        VM2:
        $python cloudlet.py service -l
        

#[support command]:

        cloudlet check

        cloudlet -v

        cloudlet -h

        cloudlet help


#[receive and restore]:

        cloudlet service -l

#[migrate]:

        cloudlet migrate [container id] -t [destionation address]



