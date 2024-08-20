# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import json
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
        rigging_references = get_rig_nspaces()
        if rigging_references:
            for rigging_reference in rigging_references:
                percent_factor = (rigging_references.index(rigging_reference), len(rigging_references))
                if rigging_reference['namespace'] in nspace_list:
                    at_least_one = True
                    export_animation(rigging_reference, frange, percent_factor, comment=comment)
            if not at_least_one:
                logger.warning("Nothing to export from namespace list : {}".format(nspace_list))
        else:
            logger.warning("No rigging references found in wizard description")
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def invoke_settings_widget():
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('animation', parent=wizard_tools.maya_main_window())
    if export_settings_widget_win.exec() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def export_animation(rigging_reference, frange, percent_factor, comment=''):
    rig_nspace = rigging_reference['namespace']
    asset_name = rigging_reference['asset_name']
    exported_string_asset = rigging_reference['string_stage']
    count = rigging_reference['count']
    if is_referenced(rig_nspace):
        export_GRP_list = get_objects_to_export(rig_nspace)
        if export_GRP_list:
            logger.info("Exporting {}".format(rig_nspace))
            additionnal_objects = wizard_export.trigger_before_export_hook('animation', exported_string_asset)
            export_GRP_list += additionnal_objects
            export_name = buid_export_name(asset_name, count)
            wizard_export.export('animation', export_name, exported_string_asset, export_GRP_list, frange, percent_factor=percent_factor, comment=comment)
        else:
            logger.warning("No objects to export in '{}:render_set'".format(rig_nspace))

def buid_export_name(asset_name, count):
    export_name = asset_name
    if count != '0':
        export_name += "_{}".format(count)
    return export_name

def get_objects_to_export(rig_nspace):
    objects_to_export = None
    render_set = "{}:render_set".format(rig_nspace)
    if pm.objExists(render_set):
        objects_to_export = pm.sets(render_set, q=True)
        if len(objects_to_export) == 0:
            logger.warning("{} is empty".format(render_set))
            objects_to_export = None
    else:
        logger.warning("{} not found".format(render_set))
    return objects_to_export

def is_referenced(rig_nspace):
    exists = False
    if pm.namespace(exists=rig_nspace):
        if pm.namespaceInfo(rig_nspace, ls=True):
            exists = True
    if not exists:
        logger.warning("{} not found in current scene".format(rig_nspace))
    return exists

def get_rig_nspaces():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        return references['rigging']
    else:
        logger.warning("No rigging references found")
        return None
