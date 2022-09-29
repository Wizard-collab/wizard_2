# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)


# Maya modules
import maya.cmds as cmds

# Wizard modules
import wizard_communicate

def create_video(*args):
	directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
	logger.info("Playblasting at {}...".format(directory))
	playblast(directory)
	wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory)

def playblast(directory):
	start = cmds.playbackOptions( q=True,min=True )
	end  = cmds.playbackOptions( q=True,max=True )
	image_format = wizard_communicate.get_image_format()
	file = os.path.join(directory, 'tmp_playblast').replace('\\', '/')
	cmds.playblast(st=start, et=end, p= 100, f=file, wh=image_format, qlt= 100, fp= 4, fmt='image', compression='png', fo=1, v=False)
