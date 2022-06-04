# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import nuke
import nukescripts

# Wizard modules
import wizard_communicate

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.debug("Saving file {}".format(file_path))
        nuke.scriptSaveAs(file_path)
        #hou.hipFile.save(file_name=file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment")

def get_all_nodes():
    return nuke.allNodes()

def get_all_nodes_names():
    nodes_names_list = []
    for node in nuke.allNodes():
        nodes_names_list.append(node['name'].value())
    return nodes_names_list

def get_new_objects(old_objects):
    all_objects = get_all_nodes()
    new_objects = []
    for object in all_objects:
        if object not in old_objects:
            new_objects.append(object)
    return new_objects

def exr_list_to_paths_list(exr_list):
    paths_list = []
    paths_dic = dict()

    for file in exr_list:
        file_tokens = file.split('.')
        frame_number = file_tokens[-2]
        digits_string = replace_digits(frame_number)
        file_tokens[-2] = digits_string
        file = ('.').join(file_tokens)

        if file not in paths_dic.keys():
            paths_dic[file] = []

        paths_dic[file].append(int(frame_number))

        paths_list.append(file)

    for path in paths_dic.keys():
        paths_dic[path].sort()
        frange = [paths_dic[path][0], paths_dic[path][-1]]
        paths_dic[path] = frange

    return paths_dic

def replace_digits(digits):
    string_digit = ''
    for token in digits:
        string_digit += '#'
    return string_digit

def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory

def unselect_all():
    for node in nuke.allNodes():
        node.setSelected(False)

def select_nodes(nodes_list):
    unselect_all()
    for node in nodes_list:
        node.setSelected(True)

def backdrop_nodes(nodes_list, name):
    select_nodes(nodes_list)
    backdrop = nukescripts.autoBackdrop()
    backdrop['name'].setValue(name)