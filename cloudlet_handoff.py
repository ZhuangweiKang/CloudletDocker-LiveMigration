#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import socket
import struct
from cloudlet_filesystem import cloudlet_filesystem
from docker import Client
from cloudlet_utl import *
import logging
import time
import commands


class cloudlet_socket:

    def __init__(self, dst_ip):
        # port is defined in cloudlet_utl.
        HOST = dst_ip
        logging.info('dst ip %s:' % HOST)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, port))
        except Exception, e:
            logging.error('Error connecting to server:%s' % e)
            return False

    def send_file(self, file_path):
        filehandle = open(file_path, 'rb')
        self.socket.sendall(filehandle.read())
        filehandle.close()

    def send(self, msg):
        length = len(msg)
        self.socket.sendall(struct.pack('!I', length))
        self.socket.sendall(msg)

    def close(self):
        self.socket.close()

    def recv(self):
        len_buf = self.socket.recv(4)      
        length, = struct.unpack('!I', len_buf)
        return self.socket.recv(length)


def get_con_info(name):
    cli = Client(version='1.26')
    out = cli.inspect_container(name)
    if 'Error' in out:
        logging.error('get container id failed')
        return None, None

    image = out['Config']['Image']
    image_id = out['Image']

    label = name + '-' + image + '-' + image_id
    logging.info(label)

    return out['Id'], label


def check_container_status(id):
    cli = Client(version='1.26')
    out = cli.containers(id)
    lines = str(out)
    if 'Id' in lines:
        logging.info('\nid get by docker-py:%s' % out[0]['Id'])
        return True

    return False


class handoff:

    def __init__(self, con, dst_ip):
        self.dst_ip = dst_ip
        self.task_id = random_str()
        self.con = con
        self.con_id, self.label = get_con_info(con)

    def run(self):
        print("\ntask id: %s" % self.task_id)
        start_time = time.time()
    
    #-----step1: send init info.
        if not check_container_status(self.con_id):
            logging.error("container is not runing,please check")
            return False

        #---: we need to know the status of destionation node.
        #   for eaxmple, CRIU version and docker version.

        clet_socket = cloudlet_socket(self.dst_ip)
        msg = 'init#' + self.task_id + '#' + self.label
        clet_socket.send(msg)
        data = clet_socket.recv()
        if 'success' not in data:
            logging.error('send init info failed\n')
            return False

    #---step2 send image info
        image_handle = cloudlet_filesystem(self.con_id, self.task_id)
        image_id = self.label.split('-')[2]
        if not image_handle.save_image(image_id):
            logging.error("saveing image file error")
            return False

        # send tar image file
        tar_image = image_handle.image_path()
        msg_image_tar = 'image#' + str(os.path.getsize(tar_image)) + '#'
        send_image_start = time.time()
        clet_socket.send(msg_image_tar)
        clet_socket.send_file(tar_image)

        data = clet_socket.recv()
        if 'success' not in data:
            return False
        else:
            send_image_end = time.time()
        print('\nsending image total time: %f' % (send_image_end - send_image_start))

    #---step3: dump container:
        ch_handle = cloudlet_filesystem(self.con_id, self.task_id)
        if not ch_handle.checkpoint():
            logging.error("extract file failed")
            return False

        con_checkpoint = ch_handle.checkpoint_path()
        msg_ch = 'checkpoint#' + str(os.path.getsize(con_checkpoint)) + '#'
        clet_socket.send(msg_ch)
        time_start = time.time()
        clet_socket.send_file(con_checkpoint)
        data = clet_socket.recv()

        if 'success' not in data:
            logging.error('send dump files failed\n')
            return False
        else:
            end_time = time.time()
        print('\nmigration total time: %f ' % (end_time - time_start))

        return True
