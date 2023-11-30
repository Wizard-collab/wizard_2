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


def main(comment=''):
    scene = wizard_tools.save_increment()
    try:
        if wizard_communicate.get_export_format(int(os.environ['wizard_work_env_id'])) == 'abc':
            out_nodes_dic = wizard_tools.get_export_nodes('wizard_grooming_output')
            if out_nodes_dic == dict():
                logger.warning("No export nodes found...")
                return
            for out_node_name in out_nodes_dic.keys():
                export_name = out_nodes_dic[out_node_name]
                asset_name = os.environ['wizard_asset_name']
                exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
                wizard_export.trigger_before_export_hook('grooming', exported_string_asset)
                wizard_export.export(stage_name='grooming', export_name=export_name, exported_string_asset=exported_string_asset, out_node=out_node_name, comment=comment)
        else:
            export_name = 'main'
            asset_name = os.environ['wizard_asset_name']
            exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
            wizard_export.trigger_before_export_hook('grooming', exported_string_asset)
            wizard_export.export(stage_name='grooming', export_name=export_name, exported_string_asset=exported_string_asset, out_node='', comment=comment)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
