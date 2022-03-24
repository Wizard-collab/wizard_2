# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from blender_wizard import wizard_tools

# Blender modules
import bpy

def main():
    export_dic = dict()

    groups_dic = {'modeling_GRP_LOD1':'LOD1',
                    'modeling_GRP_LOD2':'LOD2',
                    'modeling_GRP_LOD3':'LOD3'}
    for grp_name in groups_dic.keys():
        # Check group existence
        grp_obj = bpy.context.scene.objects.get(grp_name)
        if wizard_tools.check_obj_list_existence([grp_name]):
            grp_obj = bpy.context.scene.objects.get(grp_name)
            object_list = [grp_obj] + wizard_tools.get_all_children(grp_obj)
            objects_dic = wizard_tools.remove_LOD_from_names(object_list)
            export_name = groups_dic[grp_name]
            export_dic[export_name] = dict()
            export_dic[export_name]['stage_name'] = 'modeling'
            export_dic[export_name]['export_GRP_list'] = [grp_obj]

    return export_dic
