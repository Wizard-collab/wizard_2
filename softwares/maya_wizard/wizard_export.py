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

def export(stage_name, export_name, exported_string_asset, export_GRP_list, frange=[0,0], custom_work_env_id = None, percent_factor=(0,1), comment=''):
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
                                                int(os.environ['wizard_version_id']),
                                                comment=comment)
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def export_by_extension(export_GRP_list, export_file, frange, percent_factor):
    if export_file.endswith('.abc'):
        export_files_list = export_abc(export_GRP_list, export_file, frange, percent_factor)
    elif export_file.endswith('.ma'):
        export_files_list = export_ma(export_GRP_list, export_file)
    elif export_file.endswith('.obj'):
        export_files_list = export_obj(export_GRP_list, export_file)
    elif export_file.endswith('.fbx'):
        export_files_list = export_fbx(export_GRP_list, export_file)
    else:
        logger.info("{} extension is unkown".format(export_file))
        export_files_list = [export_file]
    return export_files_list

def export_ma(export_GRP_list, export_file):
    logger.info("Exporting .ma")
    ma_command = wizard_hooks.get_ma_command('maya')
    if ma_command is None:
        ma_command = default_ma_command
    ma_command(export_GRP_list, export_file)
    return [export_file]

def export_obj(export_GRP_list, export_file):
    logger.info("Exporting .obj")
    obj_command = wizard_hooks.get_obj_command('maya')
    if obj_command is None:
        obj_command = default_obj_command
    obj_command(export_GRP_list, export_file)
    return [export_file]

def export_fbx(export_GRP_list, export_file):
    logger.info("Exporting .fbx")
    fbx_command = wizard_hooks.get_fbx_command('maya')
    if fbx_command is None:
        fbx_command = default_fbx_command
    fbx_command(export_GRP_list, export_file)
    return [export_file]

def export_abc(export_GRP_list, export_file, frange, percent_factor):
    logger.info("Exporting .abc")
    abc_command = wizard_hooks.get_abc_command('maya')
    if abc_command is None:
        abc_command = default_abc_command
    abc_command(frange[0],
                frange[1],
                export_GRP_list,
                export_file,
                wizard_tools.by_frame_progress_script(frange, percent_factor))
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
        if os.environ["wizard_launch_mode"] == 'gui':
            wizard_communicate.screen_over_version(int(os.environ['wizard_version_id']))
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

def default_abc_command(start,
                end,
                export_GRP_list,
                export_file,
                perFrameCallback):
    abc_command = "-frameRange {start} {end} "
    abc_command += "-step 1 -frameRelativeSample -0.2 -frameRelativeSample 0 -frameRelativeSample 0.2 "
    abc_command += "-attr wizardTags "
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

def default_fbx_command(export_GRP_list,
                export_file):
    try:
        pm.loadPlugin("fbxmaya")
    except:
        logger.debug("fbxmaya plug-in already loaded") 
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.mel.FBXResetExport()
    pm.mel.FBXExportSmoothMesh(v = False)
    pm.mel.FBXExport(f=export_file, s=True)

def default_obj_command(export_GRP_list,
                export_file):
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.exportSelected(export_file, preserveReferences=0, shader=1)

def default_ma_command(export_GRP_list,
                export_file):
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.exportSelected(export_file, type='mayaAscii', pr=0)
    