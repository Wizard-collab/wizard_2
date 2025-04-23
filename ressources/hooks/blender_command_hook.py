# coding: utf-8
# Wizard commands hook

import logging

import bpy
from blender_wizard import wizard_tools

logger = logging.getLogger(__name__)


def abc_command(export_GRP_list, export_file, frange):
    ''' This function is used to store 
    a default alembic export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    wizard_tools.select_all_children(export_GRP_list)
    bpy.ops.wm.alembic_export(filepath=export_file,
                              selected=True,
                              export_custom_properties=True,
                              uvs=True,
                              orcos=True,
                              start=frange[0],
                              end=frange[1],
                              sh_open=-0.2,
                              sh_close=0.2)


def fbx_command(export_GRP_list, export_file, frange):
    ''' This function is used to store 
    a default fbx export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    wizard_tools.select_all_children(export_GRP_list)
    bpy.ops.export_scene.fbx(filepath=export_file,
                             use_selection=True,
                             use_custom_props=True)
