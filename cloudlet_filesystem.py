#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import tarfile
import shutil
import logging
from cloudlet_utl import *
import random
import commands

class cloudlet_filesystem:

    def __init__(self, con_id, task_id):
        self.con_id = con_id
        self.task_id = task_id
        self.checkpoint_tar = task_id + '-checkpoint.tar'
        self.image_tar = task_id + '-image.tar'
        
    def tar_file_without_path(self, checkpoint_tar, path):
        os.chdir(path)
        tar_file = tarfile.TarFile.open(checkpoint_tar, 'w')
        tar_file.add('./')
        tar_file.close()
        shutil.move(checkpoint_tar, self.workdir())
        os.chdir('../')

    def save_image(self, image_id):
        os.mkdir(self.workdir())

        # tar the image in work directory
        print('\nSave image %s to %s ...' % (image_id, self.image_tar))
        tar_image = 'docker save -o ' + self.workdir() + self.image_tar + ' ' + image_id
        print(os.popen(tar_image, 'r').read())

        tar_image_path = self.workdir() + self.image_tar
        # check image file exist
        if not check_dir(tar_image_path):  # check container path exist or not?
            logging.error('file path %s not exist' % tar_image_path)
            return False

        return True
    

    def checkpoint(self):
        '''
          tar dump files in  /$(container_id)/chekcpoints/$(checkpoint_id)
        '''
        # checkpointing the container
        con_path = base_dir + 'containers/' + self.con_id + '/'

        if not check_dir(con_path):  # check container path exist or not?
            logging.error('file path %s not exist' % con_path)
            return False
        checkpoint_dir = con_path + '/checkpoints/' # checkpoints path
        checkpoint_name = self.task_id + '-' + self.con_id + '-checkpoint'


        print('\nCreate checkpoint for container %s...' % self.con_id)
        cmd_option = 'docker checkpoint create ' + self.con_id + ' ' + checkpoint_name
        print(os.popen(cmd_option, 'r').read())

        cur_checkpoint_path = checkpoint_dir + checkpoint_name

        if not check_dir(cur_checkpoint_path):  # check current checkpoint path exist or not?
            logging.error('file path %s not exist' % cur_checkpoint_path)
            return False

        checkpoint_tar = self.checkpoint_tar
        
        self.tar_file_without_path(checkpoint_tar, cur_checkpoint_path)

        return True

    def workdir(self):
        return base_dir + 'tmp/' + self.task_id + '/'

    def checkpoint_path(self):
        return self.workdir() + self.checkpoint_tar

    def image_path(self):
        return self.workdir() + self.image_tar

    def untar_file_to_path(self, tar_file, path):
        tar = tarfile.TarFile.open(tar_file, 'r')
        tar.extractall(path)
        tar.close()
        os.remove(tar_file)

    def restore(self):
      
        os.chdir(self.workdir())

        checkpoint_tar = self.checkpoint_tar

        checkpoint_name = self.task_id + '-chekcpoint'
        os.mkdir(checkpoint_name)
        checkpoint_path = self.workdir() + checkpoint_name

        if not check_dir(checkpoint_path):
            logging.error('dir(%s)not exist' % checkpoint_path)
            return False

        self.untar_file_to_path(checkpoint_tar, checkpoint_path)

        print("\nStart container from dump files...")
        cmd_option = 'docker start ' + '--checkpoint-dir=' + self.workdir() + ' --checkpoint='+ checkpoint_name + ' ' + self.con_id
        print ('\nContainer %s is running on background' % self.con_id)
        print(os.popen(cmd_option, 'r').read())

        return True
