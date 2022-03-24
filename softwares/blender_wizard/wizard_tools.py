# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
import wizard_communicate

# Blender modules
import bpy

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.info("Saving file {}".format(file_path))
        bpy.ops.wm.save_as_mainfile(filepath=file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment")

def check_obj_list_existence(object_list):
    success = True
    for obj_name in object_list:
        obj = bpy.context.scene.objects.get(obj_name)
        if not obj:
            logger.warning("'{}' not found".format(obj_name))
            success = False
    return success

def get_direct_children(object): 
    children = [] 
    for ob in bpy.data.objects: 
        if ob.parent == object: 
            children.append(ob) 
    return children

def get_all_nodes():
    all_objects = []
    for node in bpy.data.objects:
        all_objects.append(node)
    for material in bpy.data.materials:
        all_objects.append(material)
    for image in bpy.data.images:
        all_objects.append(image)
    return all_objects

def get_new_objects(old_objects):
    all_objects = get_all_nodes()
    new_objects = []
    for object in all_objects:
        if object not in old_objects:
            new_objects.append(object)
    return new_objects

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

def select_GRP_list_and_all_children(GRP_list):
    bpy.ops.object.select_all(action='DESELECT')
    for GRP in GRP_list:
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