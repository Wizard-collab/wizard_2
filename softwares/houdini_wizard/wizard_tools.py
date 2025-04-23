# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Houdini modules
import hou

# Wizard modules
import wizard_communicate
import wizard_hooks

logger = logging.getLogger(__name__)


def save_increment(comment=''):
    file_path, version_id = wizard_communicate.add_version(
        int(os.environ['wizard_work_env_id']), comment=comment)
    if file_path and version_id:
        logger.debug("Saving file {}".format(file_path))
        hou.hipFile.save(file_name=file_path)
        os.environ['wizard_version_id'] = str(version_id)
        trigger_after_save_hook(file_path)
        return file_path
    else:
        logger.warning("Can't save increment")


def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('houdini', stage_name, string_asset, scene_path)


def trigger_after_scene_openning_hook():
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_scene_openning_hooks('houdini', stage_name, string_asset)


def create_node_without_duplicate(type, name, parent=None):
    if not parent:
        parent = hou.node('/obj')
    node_path = "{}/{}".format(parent.path(), name)
    node = hou.node(node_path)
    if node not in parent.children():
        node = parent.createNode(type, node_name=name)
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


def get_all_nodes(parent=hou.node('/')):
    return parent.allSubChildren()


def node_exists(name, parent=None):
    if not parent:
        parent = hou.node('/obj')
    node_path = "{}/{}".format(parent.path(), name)
    node = hou.node(node_path)
    return node


def look_for_node(name, parent=None):
    if parent is not None:
        for node in hou.node('/').allSubChildren():
            if node.name() == parent:
                parent = node
                break
    else:
        parent = hou.node('/')
    found = None
    for node in parent.allSubChildren():
        if node.name() == name:
            found = node
            break
    return found


def look_for_nodetype(node_type, parent=None):
    if parent is not None:
        for node in hou.node('/').allSubChildren():
            if node.name() == parent:
                parent = node
                break
    else:
        parent = hou.node('/')
    found = None
    for node in parent.allSubChildren():
        if node.type().name() == node_type:
            found = node
            break
    return found


def check_out_node_existence(out_node, parent=None):
    if look_for_node(out_node, parent):
        return True
    else:
        logger.warning("'{}' not found".format(out_node))
        return False


def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory


def get_new_objects(old_objects):
    all_objects = get_all_nodes()
    new_objects = []
    for object in all_objects:
        try:
            if object not in old_objects:
                new_objects.append(object)
        except hou.ObjectWasDeleted:
            pass
    return new_objects


def get_wizard_ref_node():
    wizard_ref_node_name = "wizard_references"
    obj_node = hou.node("/obj")
    wizard_ref_node = hou.node("/obj/" + wizard_ref_node_name)
    if wizard_ref_node not in obj_node.children():
        obj_node.createNode("geo", node_name=wizard_ref_node_name)
        wizard_ref_node = hou.node("/obj/" + wizard_ref_node_name)
    return wizard_ref_node


def apply_tags(out_node):
    out_node_parent = out_node.parent()
    out_node_input = out_node.inputs()[0]

    if out_node_input.name().startswith('wizardTags_'):
        return

    name = f"wizardTags_{out_node.name()}"

    tags_node = create_node_without_duplicate(
        'attribwrangle', name, out_node_parent)
    tags_node.parm('class').set('detail')

    asset_tag = "{}_{}".format(
        os.environ['wizard_category_name'], os.environ['wizard_asset_name'])
    if os.environ['wizard_variant_name'] != 'main':
        asset_tag += f"_{os.environ['wizard_variant_name']}"
    to_tag = [os.environ['wizard_category_name'], asset_tag]

    tags_list_string = (',').join(to_tag)

    tags_node.parm('snippet').set(f'''s@wizardTags += "{tags_list_string}";''')

    tags_node.setInput(0, out_node_input)
    out_node.setInput(0, tags_node)


def by_frame_progress_script(percent_factor=100):
    command = "import hou\n"
    command += "frame=hou.frame()\n"
    command += "range=hou.playbar.playbackRange()\n"
    command += "inframe=range[0]\n"
    command += "outframe=range[1]\n"
    command += "percent={}*((frame-inframe)/(outframe-inframe))\n".format(percent_factor)
    command += 'print("wizard_task_percent:{}".format(percent))\n'
    return command


def get_export_nodes(base_name, parent=hou.node('/')):
    out_nodes_dic = dict()
    tokens_len = len(base_name.split('_'))
    for node in get_all_nodes(parent=parent):
        node_name = node.name()
        short_node_name = node_name.split('|')[-1]
        if short_node_name.startswith(base_name):
            node_name_tokens = node_name.split('_')
            if len(node_name_tokens) == tokens_len:
                export_name = 'main'
            elif len(node_name_tokens) > tokens_len:
                export_name = node_name_tokens[-1]
            if export_name in out_nodes_dic.values():
                logger.warning(f'{node_name} already found.')
                continue
            out_nodes_dic[node_name] = export_name
    return out_nodes_dic
