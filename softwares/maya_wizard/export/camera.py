# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
import os
import logging

logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main():
    if 'wizard_json_settings' in os.environ.keys():
        settings_dic = json.loads(os.environ['wizard_json_settings'])
        frange = settings_dic['frange']
        refresh_assets = settings_dic['refresh_assets']
        nspace_list = settings_dic['nspace_list']

    camrig_references = get_camrig_nspaces()
    if camrig_references:
        for camrig_reference in camrig_references:
            if camrig_reference in nspace_list:
                export_camera(camrig_reference, frange)

def export_camera(camrig_reference, frange):
    camrig_nspace = camrig_reference['namespace']
    asset_name = camrig_reference['asset_name']
    variant_name = camrig_reference['variant_name']
    count = camrig_reference['count']
    if is_referenced(camrig_nspace):
        if os.environ['wizard_stage_name'] != 'camera':
            camera_work_env_id = wizard_communicate.create_or_get_camera_work_env(int(os.environ['wizard_work_env_id']))
        else:
            camera_work_env_id = int(os.environ['wizard_work_env_id'])
        export_GRP_list = get_objects_to_export(camrig_nspace)
        if export_GRP_list:
            additionnal_objects = wizard_export.trigger_before_export_hook('camera')
            export_GRP_list += additionnal_objects
            export_name = buid_export_name(asset_name, variant_name, count)
            wizard_export.export('camera', export_name, export_GRP_list, frange, custom_work_env_id = camera_work_env_id)

def buid_export_name(asset_name, variant_name, count):
    if variant_name == 'main':
        export_name = asset_name
    else:
        export_name = "{}_{}".format(asset_name, variant_name)
    if count:
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
