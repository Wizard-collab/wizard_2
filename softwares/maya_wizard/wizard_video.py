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

def invoke_settings_widget(*args):
    from PySide2 import QtWidgets, QtCore, QtGui
    from maya_wizard.widgets import video_settings_widget
    video_settings_widget_win = video_settings_widget.video_settings_widget()
    if video_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        frange = video_settings_widget_win.frange
        create_video(frange)

def create_video(frange):
	directory = wizard_communicate.request_video(int(os.environ['wizard_work_env_id']))
	logger.info("Playblasting at {}...".format(directory))
	playblast(directory, frange)
	wizard_communicate.add_video(int(os.environ['wizard_work_env_id']), directory)

def playblast(directory, frange):
	image_format = wizard_communicate.get_image_format()
	file = os.path.join(directory, 'tmp_playblast').replace('\\', '/')
	cmds.playblast(st=frange[0], et=frange[1], p= 100, f=file, wh=image_format, qlt= 100, fp= 4, fmt='image', compression='png', fo=1, v=False)
