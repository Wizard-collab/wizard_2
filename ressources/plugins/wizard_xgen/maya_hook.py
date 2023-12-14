# coding: utf-8
# Wizard hook

import logging
logger = logging.getLogger(__name__)

import pymel.core as pm
import maya.cmds as cmds
import os

def after_scene_openning(stage_name, string_asset):
    ''' This function is triggered
        when you open the software.

        The "stage_name" argument is the name
        of the exported stage

        The "string_asset" argument is the current
        asset represented as string

        The "scene_path" argument is the scene path, 
        if there is no scene, it will be 'None' '''
    pass

def after_save(stage_name, string_asset, scene_path):
    ''' This function is triggered
        after an incremental save.

        The "stage_name" argument is the name
        of the exported stage

        The "string_asset" argument is the current
        asset represented as string

        The "scene_path" argument is the saved 
        incremental file'''
    pass        

def sanity(stage_name, string_asset, exported_string_asset):
    ''' This function is triggered
        before the export and will stop the
        export process if the returned data is 
        "False"
        
        The "stage_name" argument is the name
        of the exported stage

        The "string_asset" argument is the current
        asset represented as string

        The "exported_string_asset" argument is the
        asset wizard will export represented as string'''        

    return True

def before_export(stage_name, string_asset, exported_string_asset):
    ''' This function is triggered
        before the export 

        The "stage_name" argument is the name
        of the exported stage

        The "string_asset" argument is the current
        asset represented as string

        You can return a list of objects 
        that wizard will add to the export

        The "exported_string_asset" argument is the
        asset wizard will export represented as string'''
    return []

def after_export(stage_name, export_dir, string_asset, exported_string_asset):
    ''' This function is triggered
        after the export

        The "stage_name" argument is the name
        of the exported stage

        The "export_dir" argument is the path wher wizard exported the
        file as string

        The "string_asset" argument is the current
        asset represented as string

        The "exported_string_asset" argument is the
        asset wizard just exported represented as string'''
    if stage_name == 'grooming':
        for node in pm.ls():
            relatives = pm.listRelatives(node, shapes=True)
            if len(relatives) != 1:
                continue
            if pm.nodeType(relatives[0]) != 'xgmSplineDescription':
                continue
            parents = node.getAllParents()
            parents_names = []
            for parent in parents:
                if 'grooming_GRP' in str(parent):
                    parents_names.append(str(parent))
            if len(parent) == 0:
                continue
            fur_export_name = f"{node.getName().split(':')[-1]}"
            file_path = os.path.join(export_dir, f'xgen_cache__{fur_export_name}.abc')
            command = f"-obj {node.getName()} "
            command += f"-file {file_path} "
            command += f"-df 'ogawa' "
            command += f"-fr 0 0 "
            command += f"-frs -0.2 -frs 0.2 "
            command += "-step 1 -wfw"
            cmds.xgmSplineCache(export=True, j=command)
    pass

def after_reference(stage_name, 
                        referenced_stage_name, 
                        referenced_files_dir,
                        namespace, 
                         new_objects,
                         string_asset,
                         referenced_string_asset):
    ''' This function is triggered
        after referencing from wizard

        The "stage_name" argument is the name
        of the exported stage

        The "referenced_stage_name" argument is the name
        of the referenced stage

        The "referenced_files_dir" argument is the directory where the
        referenced files comes from

        The "namespace" argument is the namespace of the reference

        The "new_objects" argument is a list of the new objects added
        to the current scene after the reference

        The "string_asset" argument is the current
        asset represented as string

        The "referenced_string_asset" argument is the
        asset wizard just imported represented as string'''
    pass