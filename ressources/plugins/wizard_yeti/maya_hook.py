# coding: utf-8
# Wizard plugin hook

import logging
logger = logging.getLogger(__name__)

import pymel.core as pm
import maya.cmds as cmds

def sanity(stage_name, string_asset, exported_string_asset):
    ''' This function is triggered
        before the export and will stop the
        export process if the returned data is 
        "False"
        
        The "stage_name" argument is the name
        of the exported stage '''
    if stage_name == 'grooming':
        # Grooming sanity
        sanity_status = True
        if not pm.objExists('yeti_scalps_set'):
            logger.warning("yeti_scalps_set not found")
            sanity_status = False
        if not pm.objExists('yeti_nodes_set'):
            logger.warning("yeti_nodes_set not found")
            sanity_status = False
        return sanity_status
    else:
        return True

def before_export(stage_name, string_asset, exported_string_asset):
    ''' This function is triggered
        before the export 

        The "stage_name" argument is the name
        of the exported stage

        You can return a list of objects 
        that wizard will add to the export '''
    if stage_name == 'grooming':
        yeti_scalps_set = pm.PyNode('yeti_scalps_set')
        yeti_nodes_set = pm.PyNode('yeti_nodes_set')
        return [yeti_scalps_set, yeti_nodes_set]
    else:
        return []

def after_export(stage_name, export_dir, string_asset, exported_string_asset):
    ''' This function is triggered
        after the export

        The "stage_name" argument is the name
        of the exported stage

        The "export_dir" argument is the path wher wizard exported the
        file as string '''
    if stage_name == 'grooming':
        yeti_nodes_list = cmds.sets( 'yeti_nodes_set', q=True )
        for yeti_node in yeti_nodes_list:
            fur_file = '{}/{}.fur'.format(export_dir, yeti_node)
            logging.info("Exporting {}...".format(fur_file))
            cmds.pgYetiCommand(yeti_node, writeCache=fur_file, range=(0,0), samples=1)

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
        to the current scene after the reference '''
    pass