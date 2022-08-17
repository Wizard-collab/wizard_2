# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from houdini_wizard import wizard_tools
from houdini_wizard import wizard_export

def main(nspace_list, frange):
    scene = wizard_export.save_or_save_increment()
    try:
        at_least_one = False
        rigging_references = get_rig_nspaces()
        if rigging_references:
            for rigging_reference in rigging_references:
                if rigging_reference['namespace'] in nspace_list:
                    at_least_one = True
                    export_cfx(rigging_reference, frange)
            if not at_least_one:
                logger.warning(f"Nothing to export from namespace list : {nspace_list}")
        else:
            logger.warning("No rigging references found in wizard description")
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def invoke_settings_widget():
    from PySide2 import QtWidgets, QtCore, QtGui
    from houdini_wizard.widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('cfx')
    if export_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def export_cfx(rigging_reference, frange):
    rig_nspace = rigging_reference['namespace']
    asset_name = rigging_reference['asset_name']
    variant_name = rigging_reference['variant_name']
    exported_string_asset = rigging_reference['string_variant']
    count = rigging_reference['count']
    if wizard_tools.look_for_node(rig_nspace):
        logger.info(f"Exporting {rig_nspace}")
        wizard_export.trigger_before_export_hook('cfx', exported_string_asset)
        export_name = buid_export_name(asset_name, variant_name, count)
        wizard_export.export(stage_name='cfx', export_name=export_name, out_node='wizard_cfx_output', exported_string_asset=exported_string_asset, frange=frange, parent=rig_nspace)
    else:
        logger.warning("{} not found in current scene".format(rig_nspace))

def buid_export_name(asset_name, variant_name, count):
    if variant_name == 'main':
        export_name = asset_name
    else:
        export_name = "{}_{}".format(asset_name, variant_name)
    if count != '0':
        export_name += "_{}".format(count)
    return export_name

def get_rig_nspaces():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    if 'rigging' in references.keys():
        return references['rigging']
    else:
        logger.warning("No rigging references found")
        return None