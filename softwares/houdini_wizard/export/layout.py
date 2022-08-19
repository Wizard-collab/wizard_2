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

# Houdini modules


def main():
    scene = wizard_export.save_or_save_increment()
    try:
        out_nodes_dic = {'wizard_layout_output_LOD1':'LOD1',
                    'wizard_layout_output_LOD2':'LOD2',
                    'wizard_layout_output_LOD3':'LOD3'}
        for out_node_name in out_nodes_dic.keys():
            if wizard_tools.check_out_node_existence(out_node_name):
                export_name = out_nodes_dic[out_node_name]
                exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
                wizard_export.trigger_before_export_hook('layout', exported_string_asset)
                wizard_export.export(stage_name='layout', export_name=export_name, exported_string_asset=exported_string_asset, out_node=out_node_name)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
