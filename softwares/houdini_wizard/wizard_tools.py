# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import hou

# Wizard modules
import wizard_communicate

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.debug("Saving file {}".format(file_path))
        hou.hipFile.save(file_name=file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment") 

def create_node_without_duplicate(type, name, parent = None):
    if not parent:
        parent = hou.node('/obj')
    node_path = "{}/{}".format(parent.path(), name)
    node = hou.node(node_path)
    if node not in parent.children():
        node = parent.createNode(type, node_name = name)
        node = hou.node(node_path)
    return node

def connect_to_input_item(node, parent, no):
    input_item_path = "{}/{}".format(parent.path(), str(no))
    input_item = hou.item(input_item_path)
    node.setInput(0, input_item)

def get_new_nodes_in_parent(parent, old_nodes_in_parent):
    parent_children = get_children(parent)
    new_nodes_in_parent = []
    for child in parent_children:
        if child not in old_nodes_in_parent:
            new_nodes_in_parent.append(child)
    return new_nodes_in_parent

def get_children(parent):
    return parent.children() 

def get_all_nodes():
    return hou.node('/').allSubChildren() 

def node_exists(name, parent = None):
    if not parent:
        parent = hou.node('/obj')
    node_path = "{}/{}".format(parent.path(), name)
    node = hou.node(node_path)
    return node

def look_for_node(name):
    root = hou.node('/')
    found = None
    for node in root.allSubChildren():
        if node.name() == name:
            found = node
            break
    return found

def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory

def get_new_objects(old_objects):
    all_objects = get_all_nodes()
    new_objects = []
    for object in all_objects:
        if object not in old_objects:
            new_objects.append(object)
    return new_objects

def get_wizard_ref_node():
    wizard_ref_node_name = "wizard_references"
    obj_node = hou.node("/obj")
    wizard_ref_node = hou.node("/obj/" + wizard_ref_node_name)
    if wizard_ref_node not in obj_node.children():
         obj_node.createNode("geo", node_name = wizard_ref_node_name)
         wizard_ref_node = hou.node("/obj/" + wizard_ref_node_name)
    return wizard_ref_node

def apply_tags(out_node):
    out_node_parent = out_node.parent()
    out_node_input = out_node.inputs()[0]

    tags_node = create_node_without_duplicate('attribcreate', 'wizardTags', out_node_parent)
    tags_node.parm('name1').set('wizardTags')
    tags_node.parm('class1').set('detail')
    tags_node.parm('type1').set('index')

    asset_tag = "{}_{}".format(os.environ['wizard_category_name'], os.environ['wizard_asset_name'])
    to_tag = [os.environ['wizard_category_name'], asset_tag]

    tags_node.parm('string1').set((',').join(to_tag))

    tags_node.setInput(0, out_node_input)
    out_node.setInput(0, tags_node)