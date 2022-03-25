# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Wizard modules
from blender_wizard import wizard_tools
from blender_wizard import wizard_export

# Blender modules
import bpy

def main():
    groups_dic = {'modeling_GRP_LOD1':'LOD1',
                    'modeling_GRP_LOD2':'LOD2',
                    'modeling_GRP_LOD3':'LOD3'}
    for grp_name in groups_dic.keys():
        if wizard_tools.check_obj_list_existence([grp_name]):
            grp_obj = bpy.context.scene.objects.get(grp_name)
            asset_name = os.environ['wizard_asset_name']
            grp_obj.name = asset_name
            object_list = [grp_obj] + wizard_tools.get_all_children(grp_obj, meshes=1)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            export_name = groups_dic[grp_name]

            export_GRP_list = [grp_obj]
            additionnal_objects = wizard_export.trigger_before_export_hook('modeling')
            export_GRP_list += additionnal_objects
            wizard_tools.apply_tags(export_GRP_list)

            wizard_export.export('modeling', export_name, export_GRP_list)
            grp_obj.name = grp_name
            wizard_tools.reassign_old_name_to_objects(objects_dic)