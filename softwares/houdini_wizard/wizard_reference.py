# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Wizard modules
import wizard_communicate
import wizard_hooks
from houdini_wizard import wizard_tools

# Houdini modules
import hou

logger = logging.getLogger(__name__)


def reference_modeling(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'MODELING', 'modeling', reference_dic['string_stage'])


def update_modeling(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'MODELING', 'modeling', reference_dic['string_stage'])


def reference_rigging(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'RIGGING', 'rigging', reference_dic['string_stage'])


def update_rigging(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'RIGGING', 'rigging', reference_dic['string_stage'])


def reference_grooming(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'GROOMING', 'grooming', reference_dic['string_stage'])


def update_grooming(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'GROOMING', 'grooming', reference_dic['string_stage'])


def reference_custom(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'CUSTOM', 'custom', reference_dic['string_stage'])


def update_custom(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'CUSTOM', 'custom', reference_dic['string_stage'])


def reference_layout(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'LAYOUT', 'layout', reference_dic['string_stage'])


def update_layout(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'LAYOUT', 'layout', reference_dic['string_stage'])


def reference_animation(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'ANIMATION', 'animation', reference_dic['string_stage'])


def update_animation(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'ANIMATION', 'animation', reference_dic['string_stage'])


def reference_cfx(reference_dic):
    import_from_extension(
        reference_dic['namespace'], reference_dic['files'], 'CFX', 'cfx', reference_dic['string_stage'])


def update_cfx(reference_dic):
    update_from_extension(
        reference_dic['namespace'], reference_dic['files'], 'CFX', 'cfx', reference_dic['string_stage'])


def reference_camera(reference_dic):
    import_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'CAMERA', 'camera', reference_dic['string_stage'])


def update_camera(reference_dic):
    update_from_extension(reference_dic['namespace'], reference_dic['files'],
                          'CAMERA', 'camera', reference_dic['string_stage'])


def import_from_extension(namespace, files_list, parent_GRP_name, stage_name, referenced_string_asset):
    old_nodes = wizard_tools.get_all_nodes()
    extension = files_list[0].split('.')[-1]
    if extension == 'abc':
        if stage_name != 'camera':
            reference_abc(namespace, files_list)
        else:
            reference_abc_camera(namespace, files_list)
    elif extension == 'hip':
        merge(namespace, files_list)
    trigger_after_reference_hook(stage_name,
                                 files_list,
                                 namespace,
                                 wizard_tools.get_new_objects(old_nodes),
                                 referenced_string_asset)


def update_from_extension(namespace, files_list, parent_GRP_name, stage_name, referenced_string_asset):
    old_nodes = wizard_tools.get_all_nodes()
    extension = files_list[0].split('.')[-1]
    if extension == 'abc':
        if stage_name != 'camera':
            update_abc(namespace, files_list)
        else:
            update_abc_camera(namespace, files_list)
    elif extension == 'hip':
        update_hip(namespace, files_list)
    trigger_after_reference_hook(stage_name,
                                 files_list,
                                 namespace,
                                 wizard_tools.get_new_objects(old_nodes),
                                 referenced_string_asset)


def reference_abc(namespace, files_list):
    if len(files_list) == 1:
        wizard_ref_node = wizard_tools.get_wizard_ref_node()
        if not wizard_tools.node_exists(namespace, parent=wizard_ref_node):
            abc_node = wizard_tools.create_node_without_duplicate(
                'alembic', namespace, wizard_ref_node)
            abc_node.parm("fileName").set(files_list[0])
            convert_node = wizard_tools.create_node_without_duplicate(
                'convert', namespace+"_convert", wizard_ref_node)
            convert_node.setInput(0, abc_node)
            null_node = wizard_tools.create_node_without_duplicate(
                'null', "OUT_"+namespace, wizard_ref_node)
            null_node.setInput(0, convert_node)
            wizard_ref_node.layoutChildren()
    else:
        logger.warning("Can't reference multiple abc files")


def update_abc(namespace, files_list):
    if len(files_list) == 1:
        wizard_ref_node = wizard_tools.get_wizard_ref_node()
        abc_node = wizard_tools.node_exists(namespace, parent=wizard_ref_node)
        if abc_node:
            abc_node.parm("fileName").set(files_list[0])
        else:
            logger.warning(f"{namespace} not found")
    else:
        logger.warning("Can't reference multiple abc files")


def update_hip(namespace, files_list):
    root = hou.node('/obj')
    if wizard_tools.node_exists(namespace, parent=root):
        logger.info(f"Can't update {files_list[0]} since it is merged")


def merge(namespace, files_list):
    if len(files_list) == 1:
        root = hou.node('/obj')
        if not wizard_tools.node_exists(namespace, parent=root):
            old_nodes_in_root = wizard_tools.get_children(root)
            hou.hipFile.merge(files_list[0])
            new_nodes_in_root = wizard_tools.get_new_nodes_in_parent(
                root, old_nodes_in_root)
            subnet = wizard_tools.create_node_without_duplicate(
                'subnet', namespace, parent=root)
            hou.moveNodesTo(new_nodes_in_root, subnet)
    else:
        logger.warning("Can't merge multiple files")


def reference_abc_camera(namespace, files_list):
    if len(files_list) == 1:
        cam_main_node = wizard_tools.create_node_without_duplicate(
            "alembicarchive", namespace)
        parameter = cam_main_node.parm('fileName')
        parameter.set(files_list[0])

        cam_main_node.parm('buildHierarchy').pressButton()
        cam_main_node.layoutChildren()

        image_format = wizard_communicate.get_image_format()
        hou_camera_node = wizard_tools.look_for_nodetype(
            'cam', parent=cam_main_node)
        if hou_camera_node is not None:
            hou_camera_node.parm("resx").set(image_format[0])
            hou_camera_node.parm("resy").set(image_format[1])
    else:
        logger.warning("Can't merge multiple files")


def update_abc_camera(namespace, files_list):
    if len(files_list) == 1:
        cam_main_node = wizard_tools.node_exists(namespace, parent=None)
        if cam_main_node:
            cam_main_node.parm("fileName").set(files_list[0])
            cam_main_node.parm('buildHierarchy').pressButton()
            image_format = wizard_communicate.get_image_format()
            hou_camera_node = wizard_tools.look_for_nodetype(
                'cam', parent=cam_main_node)
            if hou_camera_node is not None:
                hou_camera_node.parm("resx").set(image_format[0])
                hou_camera_node.parm("resy").set(image_format[1])
        else:
            logger.warning(f"{namespace} not found")
    else:
        logger.warning("Can't merge multiple files")


def trigger_after_reference_hook(referenced_stage_name,
                                 files_list,
                                 namespace,
                                 new_objects,
                                 referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('houdini',
                                       stage_name,
                                       referenced_stage_name,
                                       referenced_files_dir,
                                       namespace,
                                       new_objects,
                                       string_asset,
                                       referenced_string_asset)
