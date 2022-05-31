# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import hou

# Wizard modules
import wizard_communicate
from houdini_wizard import wizard_tools

# Hook modules
try:
    import houdini_hook
except:
    houdini_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import houdini_hook")

def export(stage_name, export_name, out_node, frange=[0,0], custom_work_env_id = None):
    if trigger_sanity_hook(stage_name):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])
        export_file = wizard_communicate.request_export(work_env_id,
                                                                export_name)
        export_by_extension(out_node, export_file, frange)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                [export_file],
                                                work_env_id,
                                                int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir)

def export_by_extension(out_node, export_file, frange):
    if export_file.endswith('.hip'):
        export_hip(export_file, frange)
    else:
        logger.info("{} extension is unkown".format(export_file))

def reopen(scene):
    hou.hipFile.load(scene, suppress_save_prompt=True)
    logger.info("Opening file {}".format(scene))

def save_or_save_increment():
    scene = hou.hipFile.path()
    if 'untitled.hip' in scene:
        wizard_tools.save_increment()
        scene = hou.hipFile.path()
    else:
        hou.hipFile.save()
        logger.info("Saving file {}".format(scene))
    return scene

def export_hip(export_file, frange):
    logger.info("Exporting .ma")
    hou.hipFile.save(file_name=export_file)

def trigger_sanity_hook(stage_name):
    # Trigger the before export hook
    if houdini_hook:
        try:
            logger.info("Trigger sanity hook")
            sanity = houdini_hook.sanity(stage_name)
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
    if houdini_hook:
        try:
            logger.info("Trigger before export hook")
        except:
            logger.info("Can't trigger before export hook")
            logger.error(str(traceback.format_exc()))

def trigger_after_export_hook(stage_name, export_dir):
    # Trigger the after export hook
    if houdini_hook:
        try:
            logger.info("Trigger after export hook")
            houdini_hook.after_export(stage_name, export_dir)
        except:
            logger.info("Can't trigger after export hook")
            logger.error(str(traceback.format_exc()))
