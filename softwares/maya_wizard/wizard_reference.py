# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Wizard modules
import wizard_hooks
import wizard_communicate
from maya_wizard import wizard_tools

# Maya modules
import pymel.core as pm

logger = logging.getLogger(__name__)


def load_plugins():
    logger.info("Loading plugins")
    pm.loadPlugin("AbcImport.dll")
    pm.loadPlugin("AbcExport.dll")


def reference_modeling(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'MODELING')
        if new_nodes is None:
            return
        trigger_after_reference_hook('modeling',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_modeling(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('modeling',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_rigging(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'RIGGING')
        if new_nodes is None:
            return
        trigger_after_reference_hook('rigging',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_rigging(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('rigging',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_grooming(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'GROOMING')
        if new_nodes is None:
            return
        trigger_after_reference_hook('grooming',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_grooming(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('grooming',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_custom(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'CUSTOM')
        if new_nodes is None:
            return
        trigger_after_reference_hook('custom',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_custom(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('custom',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_camrig(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'CAMRIG')
        if new_nodes is None:
            return
        trigger_after_reference_hook('camrig',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_camrig(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('camrig',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_layout(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'LAYOUT')
        if new_nodes is None:
            return
        trigger_after_reference_hook('layout',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_layout(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('layout',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_animation(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'ANIMATION')
        if new_nodes is None:
            return
        trigger_after_reference_hook('animation',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_animation(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('animation',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_cfx(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'CFX')
        if new_nodes is None:
            return
        trigger_after_reference_hook('cfx',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_cfx(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('cfx',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def reference_camera(reference_dic):
    old_objects = pm.ls()
    if not pm.namespace(exists=reference_dic['namespace']):
        new_nodes = create_reference(
            reference_dic['files'][0], reference_dic['namespace'], 'CAMERA')
        if new_nodes is None:
            return
        trigger_after_reference_hook('camera',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def update_camera(reference_dic):
    old_objects = pm.ls()
    if pm.namespace(exists=reference_dic['namespace']):
        new_nodes = update_reference(
            reference_dic['files'], reference_dic['namespace'])
        if new_nodes is None:
            return
        trigger_after_reference_hook('camera',
                                     reference_dic['files'],
                                     reference_dic['namespace'],
                                     new_nodes,
                                     reference_dic['string_stage'])


def create_reference(file, namespace, group):
    load_plugins()
    if not pm.objExists(group):
        pm.group(em=True, name=group)
    new_nodes = pm.createReference(file,
                                   namespace=namespace,
                                   groupName='wizard_temp_reference_node',
                                   groupReference=True,
                                   returnNewNodes=True)
    for object in pm.listRelatives('wizard_temp_reference_node'):
        pm.parent(object, group)
    pm.delete('wizard_temp_reference_node')
    return new_nodes


def update_reference(files_list, namespace):
    load_plugins()
    fileReference = pm.FileReference(namespace=namespace, refnode=True)
    if os.path.normpath(files_list[0]) == os.path.normpath(fileReference.path):
        logger.info(f"{namespace} already up to date, skipping")
        return
    return fileReference.load(files_list[0], returnNewNodes=True)


def trigger_after_reference_hook(referenced_stage_name,
                                 files_list,
                                 namespace,
                                 new_objects,
                                 referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('maya',
                                       stage_name,
                                       referenced_stage_name,
                                       referenced_files_dir,
                                       namespace,
                                       new_objects,
                                       string_asset,
                                       referenced_string_asset)
