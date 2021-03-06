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
import wizard_communicate
from maya_wizard import wizard_tools

# Hook modules
try:
    import maya_hook
except:
    maya_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import maya_hook")

def export(stage_name, export_name, export_GRP_list, frange=[0,0], custom_work_env_id = None, percent_factor=(0,1)):
    if trigger_sanity_hook(stage_name):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])
        export_file = wizard_communicate.request_export(work_env_id,
                                                                export_name)
        export_by_extension(export_GRP_list, export_file, frange, percent_factor)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                [export_file],
                                                work_env_id,
                                                int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir)

def export_by_extension(export_GRP_list, export_file, frange, percent_factor):
    if export_file.endswith('.abc'):
        export_abc(export_GRP_list, export_file, frange, percent_factor)
    elif export_file.endswith('.ma'):
        export_ma(export_GRP_list, export_file)
    else:
        logger.info("{} extension is unkown".format(export_file))

def export_ma(export_GRP_list, export_file):
    logger.info("Exporting .ma")
    pm.select(export_GRP_list, replace=True, noExpand=True)
    pm.exportSelected(export_file, type='mayaAscii', pr=0)

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

def trigger_sanity_hook(stage_name):
    # Trigger the before export hook
    if maya_hook:
        try:
            logger.info("Trigger sanity hook")
            sanity = maya_hook.sanity(stage_name)
            if not sanity:
                logger.info("Exporting cancelled due to sanity hook")
            return sanity
        except:
            logger.info("Can't trigger sanity hook")
            logger.error(str(traceback.format_exc()))
            return True
    else:
        return True

def trigger_before_export_hook(stage_name):
    # Trigger the before export hook
    if maya_hook:
        try:
            logger.info("Trigger before export hook")
            additionnal_objects = []
            objects = maya_hook.before_export(stage_name)
            if type(objects) is list:
                for object in objects:
                    if pm.objExists(object):
                        additionnal_objects.append(object)
                    else:
                        logger.warning("{} doesn't exists".format(object))
            else:
                logger.warning("The before export hook should return an object list")
            return additionnal_objects
        except:
            logger.info("Can't trigger before export hook")
            logger.error(str(traceback.format_exc()))
            return []

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if maya_hook:
        try:
            logger.info("Trigger after export hook")
            maya_hook.after_export(stage_name, export_dir)
        except:
            logger.info("Can't trigger after export hook")
            logger.error(str(traceback.format_exc()))
