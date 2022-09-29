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

def quick_playblast(*args):
	directory = wizard_communicate.get_video_folder(int(os.environ['wizard_version_id']))
	file_name = "0001"
	extension = ".avi"
	file = os.path.join(directory, file_name+extension)
	while os.path.isfile(file):
		file_name = str(int(file_name)+1).zfill(4)
		file = os.path.join(directory, file_name+extension)
	logger.info("Playblasting at {}...".format(file))
	playblast(file)

def playblast(file):
	start = cmds.playbackOptions( q=True,min=True )
	end  = cmds.playbackOptions( q=True,max=True )
	image_format = wizard_communicate.get_image_format()
	cmds.playblast(st=start, et=end, p= 100, f=file, wh=image_format, qlt= 70, fp= 4, fmt='movie', fo=1, v=1)
