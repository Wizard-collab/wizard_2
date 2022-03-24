# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Maya modules
import pymel.core as pm

# Wizard modules
import wizard_communicate

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

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

def check_obj_list_existence(object_list):
    success = True
    for obj_name in object_list:
        if not pm.objExists(obj_name):
            logger.warning("'{}' not found".format(obj_name))
            success = False
    return success

def save_increment(*args):
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.info("Saving file {}".format(file_path))
        pm.saveAs(file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment")