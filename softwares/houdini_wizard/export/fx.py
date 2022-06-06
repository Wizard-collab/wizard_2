# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from houdini_wizard import wizard_tools
from houdini_wizard import wizard_export
import wizard_communicate

def main(frange):
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        asset_name = os.environ['wizard_asset_name']
        wizard_export.trigger_before_export_hook('fx')
        wizard_export.export(stage_name='fx', export_name=export_name, out_node='wizard_fx_output', frange=frange)
    except:
        logger.error(str(traceback.format_exc()))

def invoke_settings_widget():
    from PySide2 import QtWidgets, QtCore, QtGui
    from houdini_wizard.widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('fx')
    if export_settings_widget_win.exec_() == QtWidgets.QDialog.Accepted:
        frange = export_settings_widget_win.frange
        main(frange)