# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import wizard_tools
from blender_wizard import wizard_export
from blender_wizard import wizard_reference
from blender_wizard.export import modeling
from blender_wizard.export import shading
from blender_wizard.export import layout
from blender_wizard.export import custom

def save_increment():
    wizard_tools.save_increment()

def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'modeling':
        modeling.main()
    elif stage_name == 'shading':
        shading.main()
    elif stage_name == 'layout':
        layout.main()
    elif stage_name == 'custom':
        custom.main()
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

def import_and_update_all():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    reference_texturing(references)
    reference_modeling(references)
    reference_shading(references)
    reference_layout(references)
    reference_animation(references)
    reference_camera(references)
    reference_custom(references)
    update_texturing(references)
    update_modeling(references)
    update_shading(references)
    refupdate_layout(references)
    refupdate_animation(references)
    refupdate_camera(references)
    update_custom(references)

def set_image_size():
    image_format = wizard_communicate.get_image_format()
    bpy.context.scene.render.resolution_x = image_format[0]
    bpy.context.scene.render.resolution_y = image_format[1]

def set_frame_range():
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    bpy.context.scene.frame_start = frame_range[1]
    bpy.context.scene.frame_end = frame_range[2]

def reference_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.reference_texturing(reference)

def update_texturing(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.update_texturing(reference)

def reference_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.import_modeling(reference)

def update_modeling(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.update_modeling(reference)

def reference_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for reference in references['shading']:
            wizard_reference.import_shading(reference)

def update_shading(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'shading' in references.keys():
        for reference in references['shading']:
            wizard_reference.update_shading(reference)

def reference_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.import_layout(reference)

def refupdate_layout(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'layout' in references.keys():
        for reference in references['layout']:
            wizard_reference.update_layout(reference)

def reference_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.import_animation(reference)

def refupdate_animation(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'animation' in references.keys():
        for reference in references['animation']:
            wizard_reference.update_animation(reference)

def reference_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.import_camera(reference)

def refupdate_camera(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camera' in references.keys():
        for reference in references['camera']:
            wizard_reference.update_camera(reference)

def reference_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.import_custom(reference)

def update_custom(references=None):
    if not references:
        references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'custom' in references.keys():
        for reference in references['custom']:
            wizard_reference.update_custom(reference)

