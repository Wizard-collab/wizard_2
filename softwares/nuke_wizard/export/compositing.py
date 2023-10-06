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
from nuke_wizard import wizard_tools
from nuke_wizard import wizard_export

# Nuke modules

def main(frange):
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        asset_name = os.environ['wizard_asset_name']
        exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
        wizard_export.trigger_before_export_hook('lighting', exported_string_asset)
        wizard_export.export('lighting', export_name, exported_string_asset, frange)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

def invoke_settings_widget():
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('compositing')
    if export_settings_widget_win.exec_() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(frange)
