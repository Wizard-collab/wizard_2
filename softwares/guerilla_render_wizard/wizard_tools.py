# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Wizard modules
import wizard_communicate
import wizard_hooks

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

logger = logging.getLogger(__name__)


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


def get_all_render_passes():
    rp_list = []
    for rp in Document().children(recursive=True, type="RenderPass"):
        rp_list.append(rp)
    return rp_list


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


def add_GRP(grp_name, parent=None):
    if grp_name not in get_all_nodes():
        with Modifier() as mod:
            if parent:
                mod.createnode(grp_name, parent=parent)
            else:
                mod.createnode(grp_name)
    node = get_node_from_name(grp_name)
    return node


def get_node_from_name(name):
    for node in Document().children(recursive=True):
        if node.getname() == name:
            break
    return node


def get_node_from_path(path):
    for node in Document().children(recursive=True):
        if node.getpath() == path:
            break
    return node


def save_increment(comment=''):
    file_path, version_id = wizard_communicate.add_version(
        int(os.environ['wizard_work_env_id']), comment=comment)
    if file_path and version_id:
        logger.info("Saving file {0}".format(file_path))
        Document().save(file_path)
        os.environ['wizard_version_id'] = str(version_id)
        trigger_after_save_hook(file_path)
        return file_path
    else:
        logger.warning("Can't save increment")


def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('guerilla_render', stage_name, string_asset, scene_path)


def trigger_after_scene_openning_hook():
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_scene_openning_hooks('guerilla_render', stage_name, string_asset)


def get_fur_nodes_files(files_list):
    nodes_list = []
    for file in files_list:
        if file.endswith('.fur'):
            file = file.replace(file.split('.')[-2]+'.fur', '%04d.fur')
            if file not in nodes_list:
                nodes_list.append(file)
    return nodes_list


def get_tags_for_yeti_or_vdb_node(namespace, node_name):
    tags = [node_name]
    references = wizard_communicate.get_references(
        int(os.environ['wizard_work_env_id']))
    for stage in references.keys():
        for reference in references[stage]:
            if reference['namespace'] == namespace:
                asset_name = reference['asset_name']
                category_name = reference['category_name']
                tags.append("{0}_{1}".format(category_name, asset_name))
                tags.append(category_name)
                break
    return tags


def convert_files_list_to_sequence(files_list):
    files = []
    for file in files_list:
        extension = file.split('.')[-1]
        file_name = file.split('.')[-3]
        new_name = "{0}.$04f.{1}".format(file_name, extension)
        if new_name not in files:
            files.append(new_name)
    return files


def get_export_grps(base_name):
    grp_dic = dict()
    tokens_len = len(base_name.split('_'))
    for obj in Document().children(recursive=True, type="SceneGraphNode"):
        object_name = obj.getname()
        short_object_name = object_name.split('|')[-1]
        if base_name in short_object_name:
            object_name_tokens = object_name.split('_')
            if len(object_name_tokens) == tokens_len:
                export_name = 'main'
            elif len(object_name_tokens) > tokens_len:
                export_name = object_name_tokens[-1]
            if export_name in grp_dic.values():
                logger.warning('{0} already found.'.format(object_name))
                continue
            grp_dic[object_name] = export_name
    return grp_dic
