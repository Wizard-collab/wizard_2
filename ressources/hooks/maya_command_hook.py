# coding: utf-8
# Wizard commands hook

import logging

import pymel.core as pm
import maya.cmds as cmds
import os

logger = logging.getLogger(__name__)


def abc_command(start,
                end,
                export_GRP_list,
                export_file,
                perFrameCallback):
    ''' This function is used to store 
    a default alembic export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    abc_command = "-frameRange {start} {end} "
    abc_command += "-step 1 -frameRelativeSample -0.2 -frameRelativeSample 0 -frameRelativeSample 0.2 "
    abc_command += "-attr wizardTags "
    abc_command += "-attr ObjectName "
    abc_command += "-writeVisibility "
    abc_command += "-writeUVSets -uvWrite "
    abc_command += "-worldSpace "
    abc_command += "{object_list} "
    abc_command += "-dataFormat ogawa "
    abc_command += "-file {export_file} "
    abc_command += "-pythonPerFrameCallback '{perFrameCallback}' "
    objects_list = ''
    for node in export_GRP_list:
        objects_list += " -root {}".format(node)
    abc_command = abc_command.format(start=start,
                                     end=end,
                                     object_list=objects_list,
                                     export_file=export_file,
                                     perFrameCallback=perFrameCallback)
    cmds.AbcExport(j=abc_command)


def fbx_command(export_GRP_list,
                export_file):
    ''' This function is used to store 
    a default fbx export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    try:
        pm.loadPlugin("fbxmaya")
    except:
        logger.debug("fbxmaya plug-in already loaded")
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.mel.FBXResetExport()
    pm.mel.FBXExportSmoothMesh(v=False)
    pm.mel.FBXExport(f=export_file, s=True)


def obj_command(export_GRP_list,
                export_file):
    ''' This function is used to store 
    a default obj export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.exportSelected(export_file, preserveReferences=0, shader=1)


def fur_command(export_GRP_list,
                export_file,
                start,
                end):
    ''' This function is used to store 
    a default fur export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    files_list = []
    for yeti_node in export_GRP_list:
        export_directory = os.path.dirname(export_file)
        node_name = yeti_node.split(':')[-1]
        file = os.path.join(export_directory, '{}.%04d.fur'.format(node_name))
        pm.select(yeti_node, r=True)
        cmds.pgYetiCommand(writeCache=file, range=(
            start, end), samples=3, sampleTimes="-0.2 0.0 0.2")


def ma_command(export_GRP_list,
               export_file):
    ''' This function is used to store 
    a default ma export command.
    You can modify it from here
    Be carreful on what you are modifying'''
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.exportSelected(export_file, type='mayaAscii', pr=0)
