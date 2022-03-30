# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory

def node_exists(node):
    try:
        pynode(node)
        return True
    except ValueError:
        return False

def get_all_nodes(name=True):
    nodes_list = []
    for node in Document().children(recursive=True):
        if name:
            nodes_list.append(node.getname())
        else:
            nodes_list.append(node)
    return nodes_list

def get_new_objects(old_objects):
    all_objects = get_all_nodes()
    new_objects = []
    for object in all_objects:
        if object not in old_objects:
            new_objects.append(get_node_from_name(object))
    return new_objects

def delete_all_but_list(object_list):
    for object in get_all_nodes():
        if object not in object_list:
            try:
                pynode(object).delete()
            except:
                pass
                
def check_obj_list_existence(object_list):
    success = True
    all_nodes = get_all_nodes()
    for obj_name in object_list:
        if obj_name not in all_nodes:
            logger.warning("'{0}' not found".format(obj_name))
            success = False
    return success

def add_GRP(grp_name, parent = None):
    if grp_name not in get_all_nodes():
        with Modifier() as mod:
            if parent:
                mod.createnode(grp_name, parent=parent)
            else:
                mod.createnode(grp_name)
    node = get_node_from_name(grp_name)
    return node

def get_node_from_name(name):
    nodes_list = []
    for node in Document().children(recursive=True):
        if node.getname() == name:
            break
    return node

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.info("Saving file {0}".format(file_path))
        Document().save(file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment")