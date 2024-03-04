# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import sys
import re
import shutil
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import nuke
import nukescripts

# Wizard modules
import wizard_communicate
import wizard_hooks

def save_increment(comment=''):
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']), comment=comment)
    if file_path and version_id:
        logger.debug("Saving file {}".format(file_path))
        nuke.scriptSaveAs(file_path)
        os.environ['wizard_version_id'] = str(version_id)
        trigger_after_save_hook(file_path)
        return file_path
    else:
        logger.warning("Can't save increment")

def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('nuke', stage_name, string_asset, scene_path)

def trigger_after_scene_openning_hook():
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_scene_openning_hooks('nuke', stage_name, string_asset)

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
        file_name_with_hashtags = re.sub(r'(_|\.)[0-9]+(.exr)', r'\1#####\2', file)
        digits = re.search(r'(_|\.)([0-9]+)(.exr)', file)
        if digits is not None:
            digits = int(digits.group(2))
        else:
            digits = ''
        if file_name_with_hashtags not in paths_dic.keys():
            paths_dic[file_name_with_hashtags] = []
        paths_dic[file_name_with_hashtags].append(digits)
        paths_list.append(file_name_with_hashtags)

    for file_name_with_hashtags in paths_dic.keys():
        paths_dic[file_name_with_hashtags].sort()
        frange = [paths_dic[file_name_with_hashtags][0], paths_dic[file_name_with_hashtags][-1]]
        paths_dic[file_name_with_hashtags] = frange
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

def create_read(name, namespace):
    read = nuke.nodes.Read(file='', name=name, xpos=0, ypos=-500)
    add_namespace_knob(read, namespace)
    return read

def switch_selection_to_deepRead():
    selection = nuke.selectedNodes()
    all_nodes = nuke.allNodes()
    for node in selection:
        if node.Class() == 'Read':
            new_node = nuke.nodes.DeepRead(file='', name='temp', xpos=0, ypos=-500)
            replace_node(node, new_node, all_nodes)
            new_node.setSelected(True)

def switch_selection_to_read():
    selection = nuke.selectedNodes()
    all_nodes = nuke.allNodes()
    for node in selection:
        if node.Class() == 'DeepRead':
            new_node = nuke.nodes.Read(file='', name='temp', xpos=0, ypos=-500)
            replace_node(node, new_node, all_nodes)
            new_node.setSelected(True)

def replace_node(node, new_node, all_nodes):
    for other_node in all_nodes:
        try:
            for i in range(other_node.inputs()):
                if other_node.input(i) == node:
                    other_node.setInput(i, new_node)
        except ValueError:
            pass
    add_namespace_knob(new_node, node['wizard_namespace'].value())
    set_read_data(new_node, node['file'].value(), [node['first'].value(), node['last'].value()])
    new_node.setXYpos(int(node['xpos'].value()), int(node['ypos'].value()))
    name = node['name'].value()
    nuke.delete(node)  
    new_node['name'].setValue(name)

def add_namespace_knob(node, namespace):
    namespace_knob = nuke.String_Knob('wizard_namespace', 'wizard_namespace')
    node.addKnob(namespace_knob)
    node['wizard_namespace'].setValue(namespace)
    node['wizard_namespace'].setEnabled(False)

def set_read_data(read, file_path, frange):

    read['file'].setValue(file_path)
    if frange[0] != '':
        read['first'].setValue(frange[0])
        read['origfirst'].setValue(frange[0])
    if frange[1] != '':
        read['last'].setValue(frange[1])
        read['origlast'].setValue(frange[1])

def get_all_namespaces():
    namespaces_dic = dict()
    for node in nuke.allNodes():
        try:
            namespace = node['wizard_namespace'].value()
            if namespace not in namespaces_dic.keys():
                namespaces_dic[namespace] = []
            namespaces_dic[namespace].append(node)
        except NameError:
            pass
    return namespaces_dic

def get_bouding_box(nodes_list):
    x0 = None
    x1 = None
    y0 = None
    y1 = None
    for node in nodes_list:
        xpos = node['xpos'].value()
        ypos = node['ypos'].value()
        if x0 is None or xpos < x0:
            x0 = xpos
        if x1 is None or xpos > x1:
            x1 = xpos
        if y0 is None or ypos < y0:
            y0 = ypos
        if y1 is None or ypos > y1:
            y1 = ypos
    return x0, x1, y0, y1

def align_nodes(nodes_list):
    x0, x1, y0, y1 = get_bouding_box(nuke.allNodes())
    pos = [int(x1)+250, int(y0)+250]
    for node in nodes_list:
        node.setXYpos( pos[0], pos[1] )
        pos[0] += 100

def backdrop_nodes(nodes_list, namespace, namespace_knob=False):
    x0, x1, y0, y1 = get_bouding_box(nodes_list)
    width = x1 - x0 + 200
    height = y1 - y0 + 200
    backdrop = nuke.toNode(namespace)
    if not backdrop:
        backdrop = nuke.nodes.BackdropNode(name=namespace)
    backdrop.setXYpos(int(x0-50), int(y0-50))
    backdrop['bdwidth'].setValue(width)
    backdrop['bdheight'].setValue(height)
    backdrop['tile_color'].setValue(2325008641)
    if namespace_knob:
        add_namespace_knob(backdrop, namespace)

def by_frame_progress(frange):
    current_frame = nuke.frame()
    progress = ((current_frame-frange[0])/(frange[1]-frange[0]))*100
    print(f"wizard_task_percent:{progress}")
    sys.stdout.flush()