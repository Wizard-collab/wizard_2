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

def main(nspace_list, frange):
    scene = wizard_export.save_or_save_increment()
    try:
        if wizard_communicate.get_export_format(os.environ['wizard_work_env_id']) == 'fur':
            main_fur(nspace_list, frange)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def main_fur(nspace_list, frange):
    at_least_one = False
    grooming_references = get_grooming_nspaces()
    if grooming_references:
        for grooming_reference in grooming_references:
            percent_factor = (grooming_references.index(grooming_reference), len(grooming_references))
            if grooming_reference['namespace'] in nspace_list:
                at_least_one = True
                export_fur(grooming_reference, frange, percent_factor)
        if not at_least_one:
            logger.warning("Nothing to export from namespace list : {}".format(nspace_list))
    else:
        logger.warning("No grooming references found in wizard description")
    

def invoke_settings_widget():
    from PySide2 import QtWidgets, QtCore, QtGui
    from maya_wizard.widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('cfx')
    if export_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def export_fur(grooming_reference, frange, percent_factor):
    grooming_nspace = grooming_reference['namespace']
    asset_name = grooming_reference['asset_name']
    variant_name = grooming_reference['variant_name']
    count = grooming_reference['count']
    if is_referenced(grooming_nspace):
        export_GRP_list = get_objects_to_export(grooming_nspace)
        if export_GRP_list:
            logger.info("Exporting {}".format(grooming_nspace))
            additionnal_objects = wizard_export.trigger_before_export_hook('cfx')
            export_GRP_list += additionnal_objects
            export_name = buid_export_name(asset_name, variant_name, count)
            wizard_export.export('cfx', export_name, export_GRP_list, frange, percent_factor=percent_factor)
        else:
            logger.warning("No objects to export in '{}:yeti_nodes_set'".format(grooming_nspace))

def buid_export_name(asset_name, variant_name, count):
    if variant_name == 'main':
        export_name = asset_name
    else:
        export_name = "{}_{}".format(asset_name, variant_name)
    if count != '0':
        export_name += "_{}".format(count)
    return export_name

def get_objects_to_export(grooming_nspace):
    objects_to_export = None
    yeti_nodes_set = "{}:yeti_nodes_set".format(grooming_nspace)
    if pm.objExists(yeti_nodes_set):
        objects_to_export = pm.sets(yeti_nodes_set, q=True)
        if len(objects_to_export) == 0:
            logger.warning("{} is empty".format(yeti_nodes_set))
            objects_to_export = None
    else:
        logger.warning("{} not found".format(yeti_nodes_set))
    return objects_to_export

def is_referenced(grooming_nspace):
    exists = False
    if pm.namespace(exists=grooming_nspace):
        if pm.namespaceInfo(grooming_nspace, ls=True):
            exists = True
    if not exists:
        logger.warning("{} not found in current scene".format(grooming_nspace))
    return exists

def get_grooming_nspaces():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'grooming' in references.keys():
        return references['grooming']
    else:
        logger.warning("No grooming references found")
        return None
