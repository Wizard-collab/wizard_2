# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import json
import logging
import traceback

logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main(nspace_list, frange):
    scene = wizard_export.save_or_save_increment()
    try:
        rigging_references = get_rig_nspaces()
        if rigging_references:
            for rigging_reference in rigging_references:
                if rigging_reference['namespace'] in nspace_list:
                    export_animation(rigging_reference, frange)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def invoke_settings_widget():
    from PySide2 import QtWidgets, QtCore, QtGui
    from maya_wizard.widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('animation')
    if export_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def export_animation(rigging_reference, frange):
    rig_nspace = rigging_reference['namespace']
    asset_name = rigging_reference['asset_name']
    variant_name = rigging_reference['variant_name']
    count = rigging_reference['count']
    if is_referenced(rig_nspace):
        export_GRP_list = get_objects_to_export(rig_nspace)
        if export_GRP_list:
            additionnal_objects = wizard_export.trigger_before_export_hook('animation')
            export_GRP_list += additionnal_objects
            export_name = buid_export_name(asset_name, variant_name, count)
            wizard_export.export('animation', export_name, export_GRP_list, frange)

def buid_export_name(asset_name, variant_name, count):
    if variant_name == 'main':
        export_name = asset_name
    else:
        export_name = "{}_{}".format(asset_name, variant_name)
    if count:
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
