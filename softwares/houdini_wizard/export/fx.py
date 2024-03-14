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

def main(frange, comment='', prepare_only=False):
    scene = wizard_export.save_or_save_increment()
    try:
        out_nodes_dic = wizard_tools.get_export_nodes('wizard_fx_output')
        if out_nodes_dic == dict():
            logger.warning("No export nodes found...")
            return
        for out_node_name in out_nodes_dic.keys():
            export_name = out_nodes_dic[out_node_name]
            asset_name = os.environ['wizard_asset_name']
            exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
            wizard_export.trigger_before_export_hook('fx', exported_string_asset)
            wizard_export.export(stage_name='fx', export_name=export_name, exported_string_asset=exported_string_asset, out_node=out_node_name, frange=frange, comment=comment, prepare_only=prepare_only)
    except:
        logger.error(str(traceback.format_exc()))

def invoke_settings_widget(prepare_only=False):
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('fx')
    if export_settings_widget_win.exec_() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(frange, prepare_only=prepare_only)