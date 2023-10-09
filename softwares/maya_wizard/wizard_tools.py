# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Maya modules
import pymel.core as pm

# Wizard modules
import wizard_communicate
import wizard_hooks

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory

def maya_main_window():
    from maya import OpenMayaUI as omui
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance 
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def get_new_objects(old_objects):
    new_objects = []
    all_objects = pm.ls()
    for object in all_objects:
        if object not in old_objects:
            new_objects.append(object)
    return new_objects

def rename_render_set(obj):
    if obj.name() == 'render_set':
        obj.rename('render_set')
        return
    else:
        if not pm.objExists('render_set'):
            obj.rename('render_set')
            return
        else:
            main_set = pm.PyNode('render_set')
            main_set.rename('render_set_main')
            obj.rename('render_set')
            return main_set

def reassign_old_name_to_objects(objects_dic):
    for object in objects_dic.keys():
        pm.rename(object.name(), objects_dic[object])

def get_selection_nspace_list():
    namespaces_list = []
    selection = pm.ls(sl=True)
    for object in selection:
        if object.namespace() not in namespaces_list:
            namespaces_list.append(object.namespace().replace(':', ''))
    return namespaces_list

def check_obj_list_existence(object_list):
    success = True
    for obj_name in object_list:
        if not pm.objExists(obj_name):
            logger.warning("'{}' not found".format(obj_name))
            success = False
    return success

def save_increment(comment=''):
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']), comment=comment)
    if file_path and version_id:
        logger.info("Saving file {}".format(file_path))
        pm.saveAs(file_path)
        os.environ['wizard_version_id'] = str(version_id)
        trigger_after_save_hook(file_path)
    else:
        logger.warning("Can't save increment")

def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('maya', stage_name, string_asset, scene_path)

def trigger_after_scene_openning_hook():
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_scene_openning_hooks('maya', stage_name, string_asset)

def apply_tags(object_list):
    all_objects = []
    for object in object_list:
        all_objects.append(object)
        all_objects += pm.listRelatives(object, allDescendents=True)
    for object in all_objects:
        if pm.attributeQuery('wizardTags', node=object, exists=1) == 0:
            pm.addAttr(object, ln="wizardTags", dt="string")
        existing_tags = []
        if pm.getAttr(object + '.wizardTags'):
            existing_tags = pm.getAttr(object + '.wizardTags').split(',')
        asset_tag = "{}_{}".format(os.environ['wizard_category_name'], os.environ['wizard_asset_name'])
        to_tag = [os.environ['wizard_category_name'], asset_tag, object.name().split(':')[-1].split('|')[-1]]
        tags = existing_tags + to_tag
        pm.setAttr(object + '.wizardTags', (',').join(set(tags)), type="string")

def by_frame_progress_script(frange, percent_factor):
    command = 'range = {} - {}\\n'.format(frange[1], frange[0])
    command+= 'if range != 0:\\n'
    command+= '    frame = #FRAME#-{}\\n'.format(frange[0])
    command+= '    to_add = ({}/{})*100\\n'.format(percent_factor[0], percent_factor[1])
    command+= '    factor = 1/{}\\n'.format(percent_factor[1])
    command+= '    percent = (frame/range)*100.0*factor+to_add\\n'
    command+= '    print("wizard_task_percent:{}".format(percent))\\n'
    return command

def get_export_grps(base_name):
    grp_dic = dict()
    tokens_len = len(base_name.split('_'))
    for obj in pm.ls(tr=1):
        object_name = obj.name()
        short_object_name = object_name.split('|')[-1]
        if base_name in short_object_name:
            object_name_tokens = object_name.split('_')
            if len(object_name_tokens) == tokens_len:
                export_name = 'main'
            elif len(object_name_tokens) > tokens_len:
                export_name = object_name_tokens[-1]
            if export_name in grp_dic.values():
                logger.warning(f'{object_name} already found.')
                continue
            grp_dic[object_name] = export_name
    return grp_dic
