# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Maya modules
import pymel.core as pm

def remove_LOD_from_names(object_list):
    objects_dic = dict()
    for object in object_list:
        old_name = object.name()
        for NUM in range(1,4):
            LOD = '_LOD{}'.format(str(NUM))
            if object.name().endswith(LOD):
            	object = pm.rename(object.name(), old_name.replace(LOD, ''))
        objects_dic[object] = old_name
    return objects_dic

def reassign_old_name_to_objects(objects_dic):
    for object in objects_dic.keys():
    	pm.rename(object.name(), objects_dic[object])

def get_selection_nspace_list():
    namespaces_list = []
    selection = pm.ls(sl=True)
    for object in selection:
        if object.namespace() not in namespaces_list:
            namespaces_list.append(object.namespace().replace(':', ''))
    return namespaces_list
