# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import nuke

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_tools

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
    for n in nuke.allNodes('Read'):
        n['first'].setValue(f1)
        n['last'].setValue(f2)
        n['origfirst'].setValue(f1)
        n['origlast'].setValue(f2)
    nuke.knob("root.first_frame", str(f1))
    nuke.knob("root.last_frame", str(f2))

def set_image_format():
    image_format = wizard_communicate.get_image_format()
    format = ' '.join([str(image_format[0]), str(image_format[1])])
    format_name = os.environ['wizard_project'] + '_format'
    project_format = '{} {}'.format(format, format_name)
    nuke.addFormat( project_format )
    nuke.knob('root.format', format_name)