#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import logging
import commands
import shutil
import tarfile
from cloudlet_filesystem import cloudlet_filesystem
from cloudlet_utl import *
import time


def lz4_uncompress(in_name='memory.lz4', out_name='pages-1.img'):
    cmd = 'lz4 -d ' + in_name + ' ' + out_name
    logging.info(cmd)
    sp.call(cmd, shell=True)
    os.remove(in_name)


class restore:

    """docstring for ClassName"""

    def __init__(self):
        os.chdir(base_dir + '/tmp/')

    def init_restore(self, task_id, label):
        self.task_id = task_id
        label_ar = label.split('-')
        self.con_name = label_ar[0]
        self.base_img = label_ar[1]
        self.img_id = label_ar[2]
        os.mkdir(self.task_id)
        os.chdir(self.task_id)

    def load_image(self):
        # set work dir.
        tar_image_name = self.task_id + '-image.tar'
        tar_image_path =  self.workdir() + '/' + tar_image_name
        print('\nLoad image from %s ...' % tar_image_path)
        image_load = 'docker load -i ' + tar_image_path
        print(os.popen(image_load, 'r').read())

        print('\nShow image list ...')
        ls_images = 'docker images'
        print(os.popen(ls_images, 'r').read())

    def create_con(self):
        print('\nCreate a container using image %s ...' % self.img_id)
        create_op = 'docker create --name=' + self.con_name + ' ' + self.img_id
        logging.debug(create_op)

        ret, id = commands.getstatusoutput(create_op)
        self.con_id = id
        

    def workdir(self):
        return base_dir + '/tmp/' + self.task_id

    
    def restore_con(self):
        restore_con = cloudlet_filesystem(self.con_id, self.task_id)
        if restore_con.restore() is False:
            logging.error('container restore failed\n')
            return False
        return True