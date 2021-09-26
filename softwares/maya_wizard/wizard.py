# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import pymel.core as pm

# Wizard modules
import wizard_communicate

def save_increment():
    file_path=wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path:
        pm.saveAs(file_path)

def save():
    pm.saveFile()

def set_frame_range():
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    pm.playbackOptions(animationStartTime=frame_range[1], animationEndTime=frame_range[2], minTime=frame_range[1], maxTime=frame_range[2])

def set_frame_range_with_rolls():
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))

    inframe = frame_range[1] - frame_range[0]
    outframe = frame_range[2] + frame_range[3]
    pm.playbackOptions(animationStartTime=inframe, animationEndTime=outframe, minTime=inframe, maxTime=outframe)

def set_image_format():
    image_format = wizard_communicate.get_image_format()

    width=float(image_format[0])
    height=float(image_format[1])
    dar=width/height

    pm.setAttr('defaultResolution.w', width)
    pm.setAttr('defaultResolution.h', height)
    pm.setAttr('defaultResolution.pa', 1)
    pm.setAttr('defaultResolution.dar', dar)