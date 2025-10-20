# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import bpy
from blender_wizard import wizard_export
from blender_wizard import wizard_tools
import wizard_communicate
import os
import sys
import json
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules

# Blender modules


def main(nspace_list, frange, comment=''):
    scene = wizard_export.save_or_save_increment()
    try:
        wizard_tools.set_mode_to_object()
        at_least_one = False
        camrig_references = get_camrig_nspaces()
        if camrig_references:
            for camrig_reference in camrig_references:
                percent_factor = (camrig_references.index(
                    camrig_reference), len(camrig_references))
                if camrig_reference['namespace'] in nspace_list:
                    at_least_one = True
                    print("Exporting {}".format(camrig_reference['namespace']))
                    export_camera(camrig_reference, frange,
                                  percent_factor, comment)
            if not at_least_one:
                logger.warning(
                    "Nothing to export from namespace list : {}".format(nspace_list))
        else:
            logger.warning("No camrig references found in wizard description")
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)


def invoke_settings_widget():
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget(
        'camera')
    if export_settings_widget_win.exec() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)


def export_camera(camrig_reference, frange, percent_factor, comment=''):
    camrig_nspace = camrig_reference['namespace']
    asset_name = camrig_reference['asset_name']
    exported_string_asset = camrig_reference['string_stage']
    count = camrig_reference['count']
    if is_referenced(camrig_nspace):
        if os.environ['wizard_stage_name'] != 'camera':
            camera_work_env_id = wizard_communicate.create_or_get_camera_work_env(
                int(os.environ['wizard_work_env_id']))
        else:
            camera_work_env_id = int(os.environ['wizard_work_env_id'])
        export_format = wizard_communicate.get_export_format(
            camera_work_env_id)
        export_GRP_list = get_objects_to_export(camrig_nspace)
        if export_GRP_list:
            logger.info("Exporting {}".format(camrig_nspace))
            additionnal_objects = wizard_export.trigger_before_export_hook(
                'camera', exported_string_asset)
            export_GRP_list += additionnal_objects
            if export_format == 'blend':
                export_GRP_list = [bpy.data.collections[camrig_nspace]]
            export_name = buid_export_name(asset_name, count)
            wizard_export.export('camera', export_name, exported_string_asset, export_GRP_list,
                                 frange, custom_work_env_id=camera_work_env_id, comment=comment)
        else:
            logger.warning(
                "No objects to export in '{}/render_set' collection".format(camrig_nspace))


def buid_export_name(asset_name, count):
    export_name = asset_name
    if count != '0':
        export_name += "_{}".format(count)
    return export_name


def get_objects_to_export(camrig_nspace):
    namespace_collection = bpy.data.collections[camrig_nspace]
    render_set_collection = wizard_tools.get_render_set_collection(
        namespace_collection)
    if not render_set_collection:
        logger.warning("{}/render_set not found".format(camrig_nspace))
        return

    objects_to_export = list(render_set_collection.all_objects)
    if len(objects_to_export) == 0:
        logger.warning("{} is empty".format(render_set_collection))
        return
    return objects_to_export


def is_referenced(camrig_nspace):
    if not wizard_tools.namespace_exists(camrig_nspace):
        logger.warning("{} not found in current scene".format(camrig_nspace))
        return
    return 1


def get_camrig_nspaces():
    references = wizard_communicate.get_references(
        int(os.environ['wizard_work_env_id']))
    if 'camrig' in references.keys():
        return references['camrig']
    else:
        logger.warning("No camrig references found")
        return None
