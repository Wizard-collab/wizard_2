# coding: utf-8
# Wizard commands hook

import logging
logger = logging.getLogger(__name__)

import bpy
from blender_wizard import wizard_tools

def abc_command(export_GRP_list, export_file):
  ''' This function is used to store 
    a default alembic export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    wizard_tools.select_GRP_list_and_all_children(export_GRP_list)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                      selected=True, export_custom_properties=True)
