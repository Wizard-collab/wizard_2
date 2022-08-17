# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
import wizard_hooks
from houdini_wizard import wizard_tools

# Houdini modules
import hou

def reference_modeling(namespace, files_list):
    import_from_extension(namespace, files_list, 'MODELING', 'modeling')

def update_modeling(namespace, files_list):
    update_from_extension(namespace, files_list, 'MODELING', 'modeling')

def reference_rigging(namespace, files_list):
    import_from_extension(namespace, files_list, 'RIGGING', 'rigging')

def update_rigging(namespace, files_list):
    update_from_extension(namespace, files_list, 'RIGGING', 'rigging')

def reference_custom(namespace, files_list):
    import_from_extension(namespace, files_list, 'CUSTOM', 'custom')

def update_custom(namespace, files_list):
    update_from_extension(namespace, files_list, 'CUSTOM', 'custom')

def reference_layout(namespace, files_list):
    import_from_extension(namespace, files_list, 'LAYOUT', 'layout')

def update_layout(namespace, files_list):
    update_from_extension(namespace, files_list, 'LAYOUT', 'layout')

def reference_animation(namespace, files_list):
    import_from_extension(namespace, files_list, 'ANIMATION', 'animation')

def update_animation(namespace, files_list):
    update_from_extension(namespace, files_list, 'ANIMATION', 'animation')

def reference_cfx(namespace, files_list):
    import_from_extension(namespace, files_list, 'CFX', 'cfx')

def update_cfx(namespace, files_list):
    update_from_extension(namespace, files_list, 'CFX', 'cfx')

def reference_camera(namespace, files_list):
    import_from_extension(namespace, files_list, 'CAMERA', 'camera')

def update_camera(namespace, files_list):
    update_from_extension(namespace, files_list, 'CAMERA', 'camera')

def import_from_extension(namespace, files_list, parent_GRP_name, stage_name):
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
                                    wizard_tools.get_new_objects(old_nodes))

def update_from_extension(namespace, files_list, parent_GRP_name, stage_name):
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
                                    wizard_tools.get_new_objects(old_nodes))

def reference_abc(namespace, files_list):
    if len(files_list) == 1:
        wizard_ref_node = wizard_tools.get_wizard_ref_node()
        if not wizard_tools.node_exists(namespace, parent=wizard_ref_node):
            abc_node = wizard_tools.create_node_without_duplicate('alembic', namespace, wizard_ref_node)
            abc_node.parm("fileName").set(files_list[0])
            convert_node = wizard_tools.create_node_without_duplicate('convert', namespace+"_convert", wizard_ref_node)
            convert_node.setInput(0, abc_node)
            null_node = wizard_tools.create_node_without_duplicate('null', "OUT_"+namespace, wizard_ref_node)
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
            new_nodes_in_root = wizard_tools.get_new_nodes_in_parent(root, old_nodes_in_root)
            subnet = wizard_tools.create_node_without_duplicate('subnet', namespace, parent=root)
            hou.moveNodesTo(new_nodes_in_root, subnet)
    else:
        logger.warning("Can't merge multiple files")

def reference_abc_camera(namespace, files_list):
    if len(files_list) == 1:
        cam_main_node = wizard_tools.create_node_without_duplicate("alembicarchive", namespace)
        abc_xform_node = wizard_tools.create_node_without_duplicate("alembicxform", namespace+'_xform', cam_main_node)
        abc_xform_node.parm("fileName").set(files_list[0])
        wizard_tools.connect_to_input_item(abc_xform_node, cam_main_node, 1)
        arg = abc_xform_node.parm("objectPath").menuLabels()[1]
        abc_xform_node.parm("objectPath").set(arg)
        abc_xform_node.parm("frame").setExpression("$F")
        hou_camera_node = wizard_tools.create_node_without_duplicate("cam", namespace+'_hou_cam', abc_xform_node)
        wizard_tools.connect_to_input_item(hou_camera_node, abc_xform_node, 1)
        cam_main_node.layoutChildren()
        abc_xform_node.layoutChildren()
    else:
        logger.warning("Can't merge multiple files")

def update_abc_camera(namespace, files_list):
    if len(files_list) == 1:
        cam_main_node = wizard_tools.node_exists(namespace, parent=None)
        if cam_main_node:
            abc_xform_node = wizard_tools.node_exists(namespace+'_xform', parent=cam_main_node)
            if abc_xform_node:
                abc_xform_node.parm("fileName").set(files_list[0])
            else:
                logger.warning(f"{namespace+'_xform'} not found")
        else:
            logger.warning(f"{namespace} not found")
    else:
        logger.warning("Can't merge multiple files")

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('houdini',
                                stage_name,
                                referenced_stage_name,
                                referenced_files_dir,
                                namespace,
                                new_objects,
                                string_asset)
    