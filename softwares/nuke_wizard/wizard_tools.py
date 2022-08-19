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
import wizard_hooks

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.debug("Saving file {}".format(file_path))
        nuke.scriptSaveAs(file_path)
        os.environ['wizard_version_id'] = str(version_id)
        trigger_after_save_hook(file_path)
    else:
        logger.warning("Can't save increment")

def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('nuke', stage_name, string_asset, scene_path)

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

def create_read(name, namespace):
    read = nuke.nodes.Read(file='', name=name, xpos=0, ypos=-500)
    add_namespace_knob(read, namespace)
    return read

def add_namespace_knob(node, namespace):
    namespace_knob = nuke.String_Knob('wizard_namespace', 'wizard_namespace')
    node.addKnob(namespace_knob)
    node['wizard_namespace'].setValue(namespace)
    node['wizard_namespace'].setEnabled(False)

def set_read_data(read, file_path, frange):
    read['file'].setValue(file_path)
    read['first'].setValue(frange[0])
    read['last'].setValue(frange[1])
    read['origfirst'].setValue(frange[0])
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
    pos = [int(nodes_list[0]['xpos'].value()), int(nodes_list[0]['ypos'].value())]
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
