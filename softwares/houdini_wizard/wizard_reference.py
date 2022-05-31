# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from houdini_wizard import wizard_tools

# Houdini modules
import hou
# Hook modules
try:
    import houdini_hook
except:
    houdini_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import houdini_hook")

def reference_modeling(namespace, files_list):
    import_from_extension(namespace, files_list, 'MODELING', 'modeling')

def reference_custom(namespace, files_list):
    import_from_extension(namespace, files_list, 'CUSTOM', 'custom')

def reference_layout(namespace, files_list):
    import_from_extension(namespace, files_list, 'LAYOUT', 'layout')

def reference_animation(namespace, files_list):
    import_from_extension(namespace, files_list, 'ANIMATION', 'animation')

def reference_camera(namespace, files_list):
    import_from_extension(namespace, files_list, 'CAMERA', 'camera')

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

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    # Trigger the after reference hook
    if houdini_hook:
        try:
            logger.info("Trigger after reference hook")
            houdini_hook.after_reference(stage_name,
                                        referenced_stage_name,
                                        referenced_files_dir,
                                        namespace,
                                        new_objects)
        except:
            logger.info("Can't trigger after reference hook")
            logger.error(str(traceback.format_exc()))