#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import netifaces as ni
import logging
import SocketServer  # for python 2.7,    sockerserver for python3.x
from cloudlet_restore import restore
from cloudlet_utl import *
import time
import struct


BUF_SIZE = 1024


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class cloudlet_handler(SocketServer.BaseRequestHandler):

    def recv_file(self, file_name, size):
        hd_file = open(file_name, 'wb')
        try:
            buffer = b''
            length = size
            while (length > 0):
                data = self.request.recv(length)
                if not data:
                    return False
                buffer += data
                length = size - len(buffer)

            hd_file.write(buffer)
            hd_file.close()
            return True

        except Exception as conError:
            logging.error('connection error:conError: %s' % conError)

    def send_msg(self, msg):
        length = len(msg)
        self.request.send(struct.pack('!I', length))
        self.request.send(msg)

    def recv_msg(self):
        len_buf = self.request.recv(4)
        length, = struct.unpack('!I', len_buf)
        return self.request.recv(length)

    def handle(self):
        data = self.recv_msg()
        str_array = data.split('#')
        rstore_handle = restore()
        cmd_type = str_array[0]

        start_time = time.time()

        if(cmd_type == 'init'):
            print ("------------------------------------------------------------------")
            # do init job.
            self.task_id = str_array[1]
            self.label = str_array[2]
            rstore_handle.init_restore(self.task_id, self.label)
            self.send_msg('init:success')
            logging.info("get int msg success\n")

        while(True):
            new_msg = self.recv_msg()
            str_array = new_msg.split('#')
            cmd_type = str_array[0]

            if (cmd_type == 'image'):
                image_name = self.task_id + '-image.tar'
                image_size = int(str_array[1])
                msg = 'recieve tar image file'
                if self.recv_file(image_name, image_size):
                    msg += 'success'
                else:
                    msg += 'failed'
                self.send_msg(msg)

                rstore_handle.load_image()
                rstore_handle.create_con()
                logging.info("recieve image file success\n")

                
            if (cmd_type == 'checkpoint'):
                checkpoint_name = self.task_id + '-checkpoint.tar'
                checkpoint_size = int(str_array[1])
                msg = "checkpoint:"
                if self.recv_file(checkpoint_name, checkpoint_size):
                    msg += "success"
                else:
                    msg += "failed"
                self.send_msg(msg)
                rstore_handle.restore_con()
                break
    
        cmd = 'docker ps -a '

        end_time = time.time()
        print(os.popen(cmd, 'r').read())

        print ('Total restore time %f' % (end_time - start_time))



class daemon:

    def run(self):
        host = ni.ifaddresses('ens3')[2][0]['addr']
        #port is defined in cloudlet_utl
        logging.info(host)
        server = ThreadedTCPServer((host, port), cloudlet_handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.debug(' stop by kebboard interrupt.')
            server.shutdown()
            server.server_close()
