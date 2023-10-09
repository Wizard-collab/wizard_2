# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import json
import traceback
import pymel.core as pm
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_reference
from maya_wizard import wizard_export
from maya_wizard import wizard_tools
from maya_wizard.export import modeling
from maya_wizard.export import rigging
from maya_wizard.export import grooming
from maya_wizard.export import custom
from maya_wizard.export import camrig
from maya_wizard.export import layout
from maya_wizard.export import animation
from maya_wizard.export import cfx
from maya_wizard.export import fx
from maya_wizard.export import camera

def save_increment(*args, comment=''):
    wizard_tools.save_increment(comment=comment)

def export(*args):
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'modeling':
        modeling.main()
    elif stage_name == 'rigging':
        rigging.main()
    elif stage_name == 'grooming':
        grooming.main()
    elif stage_name == 'custom':
        custom.main()
    elif stage_name == 'camrig':
        camrig.main()
    elif stage_name == 'layout':
        layout.main()
    elif stage_name == 'animation':
        animation.invoke_settings_widget()
    elif stage_name == 'cfx':
        cfx.invoke_settings_widget()
    elif stage_name == 'fx':
        fx.invoke_settings_widget()
    elif stage_name == 'camera':
        camera.invoke_settings_widget()
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

def export_camera(*args):
    camera.invoke_settings_widget()

def reference_and_update_all(*args):
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    reference_all(references=references)
    update_all(references=references)

def reference_all(*args, **kwargs):
    references = get_references(kwargs)
    reference_modeling(references=references)
    reference_rigging(references=references)
    reference_grooming(references=references)
    reference_custom(references=references)
    reference_camrig(references=references)
    reference_layout(references=references)
    reference_animation(references=references)
    reference_cfx(references=references)
    reference_camera(references=references)

def update_all(*args, **kwargs):
    references = get_references(kwargs)
    update_modeling(references=references)
    update_rigging(references=references)
    update_grooming(references=references)
    update_custom(references=references)
    update_camrig(references=references)
    update_layout(references=references)
    update_animation(references=references)
    update_cfx(references=references)
    update_camera(references=references)

def reference_modeling(*args, **kwargs):
    references = get_references(kwargs)
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.reference_modeling(reference)

def update_modeling(*args, **kwargs):
    references = get_references(kwargs)
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.update_modeling(reference)

def reference_rigging(*args, **kwargs):
    references = get_references(kwargs)
    if 'rigging' in references.keys():
        for reference in references['rigging']:
            wizard_reference.reference_rigging(reference)

def update_rigging(*args, **kwargs):
    references = get_references(kwargs)
    if 'rigging' in references.keys():
        for reference in references['rigging']:
            wizard_reference.update_rigging(reference)

def reference_grooming(*args, **kwargs):
    references = get_references(kwargs)
    if 'grooming' in references.keys():
        for reference in references['grooming']:
            wizard_reference.reference_grooming(reference)

def update_grooming(*args, **kwargs):
    references = get_references(kwargs)
    if 'grooming' in references.keys():
        for reference in references['grooming']:
            wizard_reference.update_grooming(reference)

def reference_custom(*args, **kwargs):
    references = get_references(kwargs)
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.reference_custom(reference)

def update_custom(*args, **kwargs):
    references = get_references(kwargs)
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.update_custom(reference)

def reference_camrig(*args, **kwargs):
    references = get_references(kwargs)
    if 'camrig' in references.keys():
        for reference in references['camrig']:
            wizard_reference.reference_camrig(reference)

def update_camrig(*args, **kwargs):
    references = get_references(kwargs)
    if 'camrig' in references.keys():
        for reference in references['camrig']:
            wizard_reference.update_camrig(reference)

def reference_layout(*args, **kwargs):
    references = get_references(kwargs)
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.reference_layout(reference)

def update_layout(*args, **kwargs):
    references = get_references(kwargs)
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.update_layout(reference)

def reference_animation(*args, **kwargs):
    references = get_references(kwargs)
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.reference_animation(reference)

def update_animation(*args, **kwargs):
    references = get_references(kwargs)
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.update_animation(reference)

def reference_cfx(*args, **kwargs):
    references = get_references(kwargs)
    if 'cfx' in references.keys():
        for reference in references['cfx']:
            wizard_reference.reference_cfx(reference)

def update_cfx(*args, **kwargs):
    references = get_references(kwargs)
    if 'cfx' in references.keys():
        for reference in references['cfx']:
            wizard_reference.update_cfx(reference)

def reference_camera(*args, **kwargs):
    references = get_references(kwargs)
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.reference_camera(reference)

def update_camera(*args, **kwargs):
    references = get_references(kwargs)
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.update_camera(reference)

def get_references(kwargs):
    references = None
    for key, value in kwargs.items():
        if key == 'references':
            references = value
            break
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    return references

def modify_reference_LOD(LOD):
    work_env_id = int(os.environ['wizard_work_env_id'])
    namespaces_list = wizard_tools.get_selection_nspace_list()
    if namespaces_list == []:
        logger.warning("Select a referenced mesh to switch LOD")
    else:
        wizard_communicate.modify_reference_LOD(work_env_id, LOD, namespaces_list)
        update_modeling()
        update_layout()

def LOD1(*args):
    modify_reference_LOD('LOD1')

def LOD2(*args):
    modify_reference_LOD('LOD2')

def LOD3(*args):
    modify_reference_LOD('LOD3')

def set_frame_range(*args):
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    pm.playbackOptions(animationStartTime=frame_range[1], animationEndTime=frame_range[2], minTime=frame_range[1], maxTime=frame_range[2])

def set_frame_rate(*args):
    frame_rate = wizard_communicate.get_frame_rate()
    frame_rate_string = f"{frame_rate}fps"
    try:
        pm.currentUnit(time=frame_rate_string)
    except RuntimeError:
        logger.warning(f"{frame_rate_string} doesn't exists.")

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