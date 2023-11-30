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
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main(comment=''):
    scene = wizard_tools.save_increment()
    try:
        groups_dic = wizard_tools.get_export_grps('modeling_GRP')
        if groups_dic == dict():
            logger.warning("No group to export...")
            return
        for grp_name in groups_dic.keys():
            logger.info(f"Exporting {grp_name}...")
            grp_obj = pm.PyNode(grp_name)
            asset_name = os.environ['wizard_asset_name']
            grp_obj.rename(asset_name)
            object_list = [grp_obj] + pm.listRelatives(grp_obj,
                                                        allDescendents=True)
            export_name = groups_dic[grp_name]

            exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(os.environ['wizard_work_env_id'])

            export_GRP_list = [grp_obj]
            additionnal_objects = wizard_export.trigger_before_export_hook('modeling', exported_string_asset)
            export_GRP_list += additionnal_objects
            wizard_tools.apply_tags(export_GRP_list)

            wizard_export.export('modeling', export_name, exported_string_asset, export_GRP_list, comment=comment)
            grp_obj.rename(grp_name)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)

