# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Blender modules
import bpy

def get_direct_children(object): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == object: 
            children.append(ob) 
    return children

def get_all_children(object):
    children = []
    for ob in bpy.data.objects:
        ancestor = ob
        while 1:
            ancestor = ancestor.parent
            if ancestor == None:
                break
            if ancestor == object:
                children.append(ob)
                break
    return(children)

def select_GRP_and_all_children(GRP):
    bpy.ops.object.select_all(action='DESELECT')
    GRP.select_set(True)
    for object in get_all_children(GRP):
        object.select_set(True)
    bpy.context.view_layer.objects.active = GRP

def clear_all_materials_of_selection():
    selection = bpy.context.selected_objects
    for object in get_all_children(selection):
        object.data.materials.clear()

def import_abc(file_path):
    bpy.ops.wm.alembic_import(filepath=file_path, as_background_job=False)

def remove_LOD_from_names(object_list):
    objects_dic = dict()
    for object in object_list:
        old_name = object.name
        for NUM in range(1,4):
            LOD = '_LOD{}'.format(str(NUM))
            if object.name.endswith(LOD):
                object.name = old_name.replace(LOD, '')
        objects_dic[object] = old_name
    return objects_dic

def reassign_old_name_to_objects(objects_dic):
    for object in objects_dic.keys():
        object.name = objects_dic[object]