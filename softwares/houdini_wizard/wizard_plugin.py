# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import hou

# Wizard modules
import wizard_communicate
from houdini_wizard import wizard_tools

def save_increment():
    wizard_tools.save_increment()

def set_frame_range(rolls=0):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    if rolls:
        f1 = frame_range[1] - frame_range[0]
        f2 = frame_range[2] + frame_range[3]
    else:
        f1 = frame_range[1]
        f2 = frame_range[2]
    hou.playbar.setFrameRange(f1, f2)
