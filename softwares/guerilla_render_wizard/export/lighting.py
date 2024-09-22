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
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export

def main(comment=''):
    scene = wizard_export.save_or_save_increment()
    try:
        groups_dic = wizard_tools.get_export_grps('lighting_GRP')
        if groups_dic == dict():
            logger.warning("No group to export...")
            return
        for grp_name in groups_dic.keys():
            logger.info("Exporting {0}...".format(grp_name))
            exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
            export_name = groups_dic[grp_name]
            export_GRP_node = wizard_tools.get_node_from_name(grp_name)
            asset_name = os.environ['wizard_asset_name']
            export_GRP_node.rename(asset_name)
            additionnal_objects = wizard_export.trigger_before_export_hook('lighting', exported_string_asset)
            export_objects_list = [asset_name]+additionnal_objects
            wizard_export.export('lighting', export_name, exported_string_asset, export_objects_list, comment=comment)
            export_GRP_node.rename(grp_name)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
