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

def main():
    scene = wizard_export.save_or_save_increment()
    try:
        groups_dic = {'layout_GRP_LOD1':'LOD1',
                    'layout_GRP_LOD2':'LOD2',
                    'layout_GRP_LOD3':'LOD3'}
        for grp_name in groups_dic.keys():
            if wizard_tools.check_obj_list_existence([grp_name]):
                grp_obj = pm.PyNode(grp_name)
                asset_name = os.environ['wizard_asset_name']
                grp_obj.rename(asset_name)
                object_list = [grp_obj] + pm.listRelatives(grp_obj,
                                                            allDescendents=True)
                objects_dic = wizard_tools.remove_LOD_from_names(object_list)
                export_name = groups_dic[grp_name]

                exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(os.environ['wizard_work_env_id'])

                export_GRP_list = [grp_obj]
                additionnal_objects = wizard_export.trigger_before_export_hook('layout', exported_string_asset)
                export_GRP_list += additionnal_objects
                wizard_tools.apply_tags(export_GRP_list)

                wizard_export.export('layout', export_name, exported_string_asset, [grp_obj])
                grp_obj.rename(grp_name)
                wizard_tools.reassign_old_name_to_objects(objects_dic)
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
