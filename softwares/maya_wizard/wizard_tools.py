# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Maya modules
import pymel.core as pm

# Wizard modules
import wizard_communicate

# Python modules
import os
import logging
logger = logging.getLogger(__name__)

def get_file_dir(file):
    directory = os.path.dirname(file)
    directory.replace('\\', '/')
    return directory

def get_new_objects(old_objects):
    new_objects = []
    all_objects = pm.ls()
    for object in all_objects:
        if object not in old_objects:
            new_objects.append(object)
    return new_objects

def remove_LOD_from_names(object_list):
    objects_dic = dict()
    for object in object_list:
        old_name = object.name()
        for NUM in range(1,4):
            LOD = '_LOD{}'.format(str(NUM))
            if object.name().endswith(LOD):
                try:
                    object = pm.rename(object.name(), old_name.replace(LOD, ''))
                    objects_dic[object] = old_name
                except:
                    logger.warning("Can't rename {}".format(object.name()))
    return objects_dic

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

def save_increment(*args):
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.info("Saving file {}".format(file_path))
        pm.saveAs(file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment")

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
    command = f'range = {frange[1]} - {frange[0]}\\n'
    command+= f'if range != 0:\\n'
    command+= f'    frame = #FRAME#-{frange[0]}\\n'
    command+= f'    to_add = ({percent_factor[0]}/{percent_factor[1]})*100\\n'
    command+= f'    factor = 1/{percent_factor[1]}\\n'
    command+= f'    percent = (frame/range)*100.0*factor+to_add\\n'
    command+= '    print("wizard_task_percent:{}".format(percent))\\n'
    return command
