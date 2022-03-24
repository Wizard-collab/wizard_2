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

# Hook modules
try:
    import blender_hook
except:
    blender_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import blender_hook")

def export(stage_name, export_name, export_GRP_list):
    if trigger_sanity_hook(stage_name):
        additionnal_objects = trigger_before_export_hook(stage_name)
        export_GRP_list += additionnal_objects
        export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                    export_name)
        if export_file.endswith('.abc'):
            export_abc(export_GRP_list, export_file)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_version_id']))
        trigger_after_export_hook(stage_name, export_dir)

def export_abc(export_GRP_list, export_file):
    wizard_tools.select_GRP_list_and_all_children(export_GRP_list)
    bpy.ops.wm.alembic_export(filepath=export_file, 
                      selected=True)

def reopen(scene):
    bpy.ops.wm.open_mainfile(filepath=scene)
    logger.info("Opening file {}".format(scene))

def save_or_save_increment():
    scene = bpy.data.filepath
    if scene == '':
        wizard_tools.save_increment()
        scene = bpy.data.filepath
    else:
        bpy.ops.wm.save_as_mainfile(filepath=scene)
        logger.info("Saving file {}".format(scene))
    return scene

def trigger_sanity_hook(stage_name):
    # Trigger the before export hook
    if blender_hook:
        try:
            logger.info("Trigger sanity hook")
            sanity = blender_hook.sanity(stage_name)
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
    if blender_hook:
        try:
            logger.info("Trigger before export hook")
            additionnal_objects = []
            objects = blender_hook.before_export(stage_name)
            if type(objects) is list:
                for object in objects:
                    if wizard_tools.check_obj_list_existence([object]):
                        additionnal_objects.append(bpy.context.scene.objects.get(object))
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
    if blender_hook:
        try:
            logger.info("Trigger after export hook")
            blender_hook.after_export(stage_name, export_dir)
        except:
            logger.info("Can't trigger after export hook")
            logger.error(str(traceback.format_exc()))
