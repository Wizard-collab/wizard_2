# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Blender modules
import bpy

# Wizard modules
import wizard_communicate
from blender_wizard import wizard_tools

def export(export_file, stage_name, export_name):
    if stage_name == 'modeling':
        export_modeling(export_file, export_name)

def export_modeling(export_file, export_name):
    GRP_NAME = 'modeling_GRP'
    # Check group existence
    GRP_OBJ = bpy.context.scene.objects.get(GRP_NAME)
    if GRP_OBJ:
        if export_file.endswith('.abc'):
            export_abc(GRP_OBJ, export_file)
        wizard_communicate.add_export_version(export_name, [export_file], int(os.environ['wizard_version_id']))
    else:
        logger.warning(f"{GRP_NAME} not found")

def export_abc(export_GRP, export_file):
    wizard_tools.select_GRP_and_all_children(export_GRP)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                      selected=True)

