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

def save_increment():
    wizard_tools.save_increment()

def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'modeling':
        modeling.main()
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

def set_image_size():
    image_format = wizard_communicate.get_image_format()
    bpy.context.scene.render.resolution_x = image_format[0]
    bpy.context.scene.render.resolution_y = image_format[1]

def reference_texturing():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.reference_texturing(reference)

def update_texturing():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'texturing' in references.keys():
        for reference in references['texturing']:
            wizard_reference.update_texturing(reference)

def reference_modeling():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'modeling' in references.keys():
        for reference in references['modeling']:
            wizard_reference.import_modeling_hard(reference)