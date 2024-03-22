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

def main(comment='', prepare_only=False):
    scene = wizard_export.save_or_save_increment()
    try:
        out_nodes_dic = wizard_tools.get_export_nodes('wizard_modeling_output')
        if out_nodes_dic == dict():
            logger.warning("No export nodes found...")
            return
        for out_node_name in out_nodes_dic.keys():
            logger.info(f"Exporting {out_node_name}...")
            export_name = out_nodes_dic[out_node_name]
            exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
            wizard_export.trigger_before_export_hook('modeling', exported_string_asset)
            wizard_export.export(stage_name='modeling', export_name=export_name, exported_string_asset=exported_string_asset, out_node=out_node_name, comment=comment, prepare_only=prepare_only)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        pass
        #wizard_export.reopen(scene)
