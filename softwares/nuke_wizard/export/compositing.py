# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging

# Wizard modules
import wizard_communicate
from nuke_wizard import wizard_tools
from nuke_wizard import wizard_export

logger = logging.getLogger(__name__)


def main(frange, comment='', prepare_only=False):
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        asset_name = os.environ['wizard_asset_name']
        exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(
            int(os.environ['wizard_work_env_id']))
        wizard_export.trigger_before_export_hook(
            'lighting', exported_string_asset)
        wizard_export.export('lighting', export_name,
                             exported_string_asset, frange, comment=comment, prepare_only=prepare_only)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        if not prepare_only:
            wizard_export.reopen(scene)


def invoke_settings_widget(prepare_only=False):
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget(
        'compositing')
    if export_settings_widget_win.exec() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(frange, prepare_only=prepare_only)
