# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

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
            object_list = [grp_obj] + wizard_tools.get_all_children(grp_obj)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            export_name = groups_dic[grp_name]
            wizard_export.export('modeling', export_name, [grp_obj])
            wizard_tools.reassign_old_name_to_objects(objects_dic)