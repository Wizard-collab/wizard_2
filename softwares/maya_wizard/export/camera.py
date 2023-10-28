# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main(nspace_list, frange, comment=''):
    scene = wizard_export.save_or_save_increment()
    try:
        at_least_one = False
        camrig_references = get_camrig_nspaces()
        if camrig_references:
            for camrig_reference in camrig_references:
                if camrig_reference['namespace'] in nspace_list:
                    at_least_one = True
                    export_camera(camrig_reference, frange, comment=comment)
            if not at_least_one:
                logger.warning("Nothing to export from namespace list : {}".format(nspace_list))
        else:
            logger.warning("No camrig references found in wizard description")
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def invoke_settings_widget():
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('camera', parent=wizard_tools.maya_main_window())
    if export_settings_widget_win.exec_() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def export_camera(camrig_reference, frange, comment=''):
    camrig_nspace = camrig_reference['namespace']
    asset_name = camrig_reference['asset_name']
    exported_string_asset = camrig_reference['string_stage']
    count = camrig_reference['count']
    if is_referenced(camrig_nspace):
        if os.environ['wizard_stage_name'] != 'camera':
            camera_work_env_id = wizard_communicate.create_or_get_camera_work_env(int(os.environ['wizard_work_env_id']))
        else:
            camera_work_env_id = int(os.environ['wizard_work_env_id'])
        export_GRP_list = get_objects_to_export(camrig_nspace)
        if export_GRP_list:
            logger.info("Exporting {}".format(camrig_nspace))
            additionnal_objects = wizard_export.trigger_before_export_hook('camera', exported_string_asset)
            export_GRP_list += additionnal_objects
            export_name = buid_export_name(asset_name, count)
            wizard_export.export('camera', export_name, exported_string_asset, export_GRP_list, frange, custom_work_env_id = camera_work_env_id, comment=comment)
        else:
            logger.warning("No objects to export in '{}:render_set'".format(camrig_nspace))

def buid_export_name(asset_name, count):
    export_name = asset_name
    if count != '0':
        export_name += "_{}".format(count)
    return export_name

def get_objects_to_export(camrig_nspace):
    objects_to_export = None
    render_set = "{}:render_set".format(camrig_nspace)
    if pm.objExists(render_set):
        objects_to_export = pm.sets(render_set, q=True)
        if len(objects_to_export) == 0:
            logger.warning("{} is empty".format(render_set))
            objects_to_export = None
    else:
        logger.warning("{} not found".format(render_set))
    return objects_to_export

def is_referenced(camrig_nspace):
    exists = False
    if pm.namespace(exists=camrig_nspace):
        if pm.namespaceInfo(camrig_nspace, ls=True):
            exists = True
    if not exists:
        logger.warning("{} not found in current scene".format(camrig_nspace))
    return exists

def get_camrig_nspaces():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'camrig' in references.keys():
        return references['camrig']
    else:
        logger.warning("No camrig references found")
        return None
