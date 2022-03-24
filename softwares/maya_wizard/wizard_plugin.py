# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import pymel.core as pm

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_reference
from maya_wizard import wizard_export
from maya_wizard import wizard_tools

def save_increment(*args):
    wizard_tools.save_increment()

def export(*args):
    stage_name = os.environ['wizard_stage_name']
    wizard_export.main(stage_name)

def reference_modeling(*args):
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def update_modeling(*args):
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.update_modeling(modeling_reference['namespace'], modeling_reference['files'])

def modify_modeling_reference_LOD(LOD):
    work_env_id = int(os.environ['wizard_work_env_id'])
    namespaces_list = wizard_tools.get_selection_nspace_list()
    wizard_communicate.modify_modeling_reference_LOD(work_env_id, LOD, namespaces_list)
    update_modeling()

def LOD1(*args):
    modify_modeling_reference_LOD('LOD1')

def LOD2(*args):
    modify_modeling_reference_LOD('LOD2')

def LOD3(*args):
    modify_modeling_reference_LOD('LOD3')

def reference_rigging(*args):
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        for modeling_reference in references['rigging']:
            wizard_reference.reference_rigging(modeling_reference['namespace'], modeling_reference['files'])

def update_rigging(*args):
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        for modeling_reference in references['rigging']:
            wizard_reference.update_rigging(modeling_reference['namespace'], modeling_reference['files'])

def set_frame_range(*args):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    pm.playbackOptions(animationStartTime=frame_range[1], animationEndTime=frame_range[2], minTime=frame_range[1], maxTime=frame_range[2])

def set_frame_range_with_rolls(*args):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))

    inframe = frame_range[1] - frame_range[0]
    outframe = frame_range[2] + frame_range[3]
    pm.playbackOptions(animationStartTime=inframe, animationEndTime=outframe, minTime=inframe, maxTime=outframe)

def set_image_format(*args):
    image_format = wizard_communicate.get_image_format()

    width=float(image_format[0])
    height=float(image_format[1])
    dar=width/height

    pm.setAttr('defaultResolution.w', width)
    pm.setAttr('defaultResolution.h', height)
    pm.setAttr('defaultResolution.pa', 1)
    pm.setAttr('defaultResolution.dar', dar)