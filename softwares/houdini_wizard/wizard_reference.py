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

def reference_animation(namespace, files_list):
    import_from_extension(namespace, files_list, 'ANIMATION', 'animation')

def import_from_extension(namespace, files_list, parent_GRP_name, stage_name):
    wizard_ref_node = wizard_tools.get_wizard_ref_node()
    if not wizard_tools.node_exists(namespace, parent=wizard_ref_node):
        old_nodes = wizard_tools.get_all_nodes()
        extension = files_list[0].split('.')[-1]
        if extension == 'abc':
            reference_abc(namespace, files_list)
        elif extension == 'hip':
            merge(namespace, files_list)
        trigger_after_reference_hook(stage_name,
                                        files_list,
                                        namespace,
                                        wizard_tools.get_new_objects(old_nodes))

def reference_abc(namespace, files_list):
    if len(files_list) == 1:
        wizard_ref_node = wizard_tools.get_wizard_ref_node()
        abc_node = wizard_tools.create_node_without_duplicate('alembic', namespace, wizard_ref_node)
        abc_node.parm("fileName").set(files_list[0])
        convert_node = wizard_tools.create_node_without_duplicate('convert', namespace+"_convert", wizard_ref_node)
        convert_node.setInput(0, abc_node)
        null_node = wizard_tools.create_node_without_duplicate('null', namespace+"_null", wizard_ref_node)
        null_node.setInput(0, convert_node)
        wizard_ref_node.layoutChildren()
    else:
        logger.warning("Can't reference multiple abc files")

def merge(namespace, files_list):
    if len(files_list) == 1:
        wizard_ref_node = wizard_tools.get_wizard_ref_node()
        hou.hipFile.merge(files_list[0])
        wizard_tools.create_node_without_duplicate('null', namespace, parent=wizard_ref_node)
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