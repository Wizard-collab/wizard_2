# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from maya_wizard import wizard_tools

# Maya modules
import pymel.core as pm

# Hook modules
try:
    import maya_hook
except:
    maya_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import maya_hook")

def reference_modeling(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'MODELING')
        trigger_after_reference_hook('modeling',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_modeling(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('modeling',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def reference_rigging(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'RIGGING')
        trigger_after_reference_hook('rigging',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_rigging(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('rigging',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def reference_custom(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'CUSTOM')
        trigger_after_reference_hook('custom',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_custom(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('custom',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def reference_camrig(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'CAMRIG')
        trigger_after_reference_hook('camrig',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_camrig(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('camrig',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def reference_layout(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'LAYOUT')
        trigger_after_reference_hook('layout',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_layout(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('layout',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def reference_animation(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'ANIMATION')
        trigger_after_reference_hook('animation',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_animation(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('animation',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def reference_camera(namespace, files_list):
    old_objects = pm.ls()
    if not pm.namespace(exists=namespace):
        create_reference(files_list[0], namespace, 'CAMERA')
        trigger_after_reference_hook('camera',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def update_camera(namespace, files_list):
    old_objects = pm.ls()
    if pm.namespace(exists=namespace):
        update_reference(namespace, files_list)
        trigger_after_reference_hook('camera',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def create_reference(file, namespace, group):
    if not pm.objExists(group):
        pm.group( em=True, name=group )
    pm.createReference(file,
                        namespace=namespace,
                        groupName='wizard_temp_reference_node',
                        groupReference=True)
    for object in pm.listRelatives('wizard_temp_reference_node'):
        pm.parent(object, group)
    pm.delete('wizard_temp_reference_node')

def update_reference(namespace, files_list):
    references = pm.listReferences(namespaces=True)
    for reference in references:
        if reference[0] == namespace:
            if os.path.normpath(files_list[0]) != os.path.normpath(reference[1].path):
                reference[1].load(files_list[0])

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    # Trigger the after export hook
    if maya_hook:
        try:
            logger.info("Trigger after reference hook")
            maya_hook.after_reference(stage_name,
                                        referenced_stage_name,
                                        referenced_files_dir,
                                        namespace,
                                        new_objects)
        except:
            logger.info("Can't trigger after reference hook")
            logger.error(str(traceback.format_exc()))

    