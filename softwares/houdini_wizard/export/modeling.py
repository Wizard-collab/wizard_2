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

# Houdini modules


def main():
    scene = wizard_export.save_or_save_increment()
    try:
        out_nodes_dic = {'wizard_modeling_output_LOD1':'LOD1',
                    'wizard_modeling_output_LOD2':'LOD2',
                    'wizard_modeling_output_LOD3':'LOD3'}
        for out_node_name in out_nodes_dic.keys():
            if wizard_tools.check_out_node_existence(out_node_name):
                export_name = out_nodes_dic[out_node_name]
                wizard_export.trigger_before_export_hook('modeling')
                wizard_export.export(stage_name='modeling', export_name=export_name, out_node=out_node_name)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
