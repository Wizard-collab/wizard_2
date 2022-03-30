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
from maya_wizard.export import custom
from maya_wizard.export import camrig
from maya_wizard.export import layout
from maya_wizard.export import animation
from maya_wizard.export import camera

def save_increment(*args):
    wizard_tools.save_increment()

def export(*args):
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'modeling':
        modeling.main()
    elif stage_name == 'rigging':
        rigging.main()
    elif stage_name == 'custom':
        custom.main()
    elif stage_name == 'camrig':
        camrig.main()
    elif stage_name == 'layout':
        layout.main()
    elif stage_name == 'animation':
        animation.invoke_settings_widget()
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
    reference_custom(references=references)
    reference_camrig(references=references)
    reference_layout(references=references)
    reference_animation(references=references)
    reference_camera(references=references)

def update_all(*args, **kwargs):
    references = get_references(kwargs)
    update_modeling(references=references)
    update_rigging(references=references)
    update_custom(references=references)
    update_camrig(references=references)
    update_layout(references=references)
    update_animation(references=references)
    update_camera(references=references)

def reference_modeling(*args, **kwargs):
    references = get_references(kwargs)
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.reference_modeling(modeling_reference['namespace'], modeling_reference['files'])

def update_modeling(*args, **kwargs):
    references = get_references(kwargs)
    if 'modeling' in references.keys():
        for modeling_reference in references['modeling']:
            wizard_reference.update_modeling(modeling_reference['namespace'], modeling_reference['files'])

def reference_rigging(*args, **kwargs):
    references = get_references(kwargs)
    if 'rigging' in references.keys():
        for rigging_reference in references['rigging']:
            wizard_reference.reference_rigging(rigging_reference['namespace'], rigging_reference['files'])

def update_rigging(*args, **kwargs):
    references = get_references(kwargs)
    if 'rigging' in references.keys():
        for rigging_reference in references['rigging']:
            wizard_reference.update_rigging(rigging_reference['namespace'], rigging_reference['files'])

def reference_custom(*args, **kwargs):
    references = get_references(kwargs)
    if 'custom' in references.keys():
        for custom_reference in references['custom']:
            wizard_reference.reference_custom(custom_reference['namespace'], custom_reference['files'])

def update_custom(*args, **kwargs):
    references = get_references(kwargs)
    if 'custom' in references.keys():
        for custom_reference in references['custom']:
            wizard_reference.update_custom(custom_reference['namespace'], custom_reference['files'])

def reference_camrig(*args, **kwargs):
    references = get_references(kwargs)
    if 'camrig' in references.keys():
        for camrig_reference in references['camrig']:
            wizard_reference.reference_camrig(camrig_reference['namespace'], camrig_reference['files'])

def update_camrig(*args, **kwargs):
    references = get_references(kwargs)
    if 'camrig' in references.keys():
        for camrig_reference in references['camrig']:
            wizard_reference.update_camrig(camrig_reference['namespace'], camrig_reference['files'])

def reference_layout(*args, **kwargs):
    references = get_references(kwargs)
    if 'layout' in references.keys():
        for layout_reference in references['layout']:
            wizard_reference.reference_layout(layout_reference['namespace'], layout_reference['files'])

def update_layout(*args, **kwargs):
    references = get_references(kwargs)
    if 'layout' in references.keys():
        for layout_reference in references['layout']:
            wizard_reference.update_layout(layout_reference['namespace'], layout_reference['files'])

def reference_animation(*args, **kwargs):
    references = get_references(kwargs)
    if 'animation' in references.keys():
        for animation_reference in references['animation']:
            wizard_reference.reference_animation(animation_reference['namespace'], animation_reference['files'])

def update_animation(*args, **kwargs):
    references = get_references(kwargs)
    if 'animation' in references.keys():
        for animation_reference in references['animation']:
            wizard_reference.update_animation(animation_reference['namespace'], animation_reference['files'])

def reference_camera(*args, **kwargs):
    references = get_references(kwargs)
    if 'camera' in references.keys():
        for camera_reference in references['camera']:
            wizard_reference.reference_camera(camera_reference['namespace'], camera_reference['files'])

def update_camera(*args, **kwargs):
    references = get_references(kwargs)
    if 'camera' in references.keys():
        for camera_reference in references['camera']:
            wizard_reference.update_camera(camera_reference['namespace'], camera_reference['files'])

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