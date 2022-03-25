# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Wizard modules
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main():
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

            export_GRP_list = [grp_obj]
            additionnal_objects = wizard_export.trigger_before_export_hook('layout')
            export_GRP_list += additionnal_objects
            wizard_tools.apply_tags(export_GRP_list)

            wizard_export.export('layout', export_name, [grp_obj])
            grp_obj.rename(grp_name)
            wizard_tools.reassign_old_name_to_objects(objects_dic)
