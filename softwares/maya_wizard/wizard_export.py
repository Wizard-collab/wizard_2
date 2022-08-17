# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Maya modules
import pymel.core as pm
import maya.cmds as cmds

# Wizard modules
import wizard_hooks
import wizard_communicate
from maya_wizard import wizard_tools

def export(stage_name, export_name, exported_string_asset, export_GRP_list, frange=[0,0], custom_work_env_id = None, percent_factor=(0,1)):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])
        export_file = wizard_communicate.request_export(work_env_id,
                                                                export_name)
        export_files_list = export_by_extension(export_GRP_list, export_file, frange, percent_factor)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                export_files_list,
                                                work_env_id,
                                                int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def export_by_extension(export_GRP_list, export_file, frange, percent_factor):
    if export_file.endswith('.abc'):
        export_files_list = export_abc(export_GRP_list, export_file, frange, percent_factor)
    elif export_file.endswith('.ma'):
        export_files_list = export_ma(export_GRP_list, export_file)
    elif export_file.endswith('.fur'):
        export_files_list = export_fur(export_GRP_list, export_file, frange, percent_factor)
    else:
        logger.info("{} extension is unkown".format(export_file))
        export_files_list = [export_file]
    return export_files_list

def export_ma(export_GRP_list, export_file):
    logger.info("Exporting .ma")
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.exportSelected(export_file, type='mayaAscii', pr=0)

    return [export_file]

def export_fur(export_GRP_list, export_file, frange, percent_factor):
    logger.info("Exporting .fur")
    files_list = []
    for yeti_node in export_GRP_list:
        export_directory = os.path.dirname(export_file)
        node_name = yeti_node.split(':')[-1]
        file = os.path.join(export_directory, '{}.%04d.fur'.format(node_name))
        pm.select(yeti_node, r=True)
        cmds.pgYetiCommand(writeCache=file, range=(frange[0], frange[-1]), samples=3, sampleTimes= "-0.2 0.0 0.2")
        
        #current_percent = float(percent) + (100.0/int(len_nspacelist))/2
        #print('percent:{}'.format(current_percent))

    for file in os.listdir(export_directory):
        files_list.append(os.path.join(export_directory, file))

    return files_list


def export_abc(export_GRP_list, export_file, frange, percent_factor):
    logger.info("Exporting .abc")
    start = str(frange[0])
    end = str(frange[1])
    command = "-frameRange "
    command += start
    command += " "
    command += end
    command += " -step 1"
    command += " -frameRelativeSample -0.2 -frameRelativeSample 0 -frameRelativeSample 0.2 -attr wizardTags -writeVisibility -writeUVSets -uvWrite -worldSpace "
    for object in export_GRP_list:
        command += " -root {}".format(object)
    command += " -dataFormat ogawa -file "
    command += export_file
    command += " -pythonPerFrameCallback '{}'".format(wizard_tools.by_frame_progress_script(frange, percent_factor))
    cmds.AbcExport(j=command)
    return [export_file]

def reopen(scene):
    pm.openFile(scene, force=True)
    logger.info("Opening file {}".format(scene))

def save_or_save_increment():
    scene = pm.sceneName()
    if scene == '':
        wizard_tools.save_increment()
        scene = pm.sceneName()
    else:
        pm.saveFile(force=True)
        logger.info("Saving file {}".format(scene))
    return scene

def trigger_sanity_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.sanity_hooks('maya', stage_name, string_asset, exported_string_asset)

def trigger_before_export_hook(stage_name, exported_string_asset):
    additionnal_objects = []
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    nodes = wizard_hooks.before_export_hooks('maya', stage_name, string_asset, exported_string_asset)
    for node in nodes:
        if pm.objExists(node):
            additionnal_objects.append(node)
        else:
            logger.warning("{} doesn't exists".format(node))
    return additionnal_objects

def trigger_after_export_hook(stage_name, export_dir, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks('maya', stage_name, export_dir, string_asset, exported_string_asset)
