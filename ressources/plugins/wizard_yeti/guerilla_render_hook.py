# coding: utf-8
# Wizard plugin hook

import os

import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_tools

# Guerilla render modules
from guerilla import Document, Modifier, pynode, Node, Plug

def add_yeti_fur(namespace, referenced_stage_name, file):
    GRP = wizard_tools.add_GRP(referenced_stage_name.upper())
    with Modifier() as mod:
        namespace_GRP = wizard_tools.add_GRP(namespace, GRP)
        fur_name = os.path.basename(file).split('.fur')[0]
        node_name = '{0}:{1}'.format(namespace, fur_name)
        if node_name not in wizard_tools.get_all_nodes():
            yeti_node = mod.createnode(node_name, "Yeti", namespace_GRP)
            yeti_node.HierarchyMode.set(2)
            tags = wizard_tools.get_tags_for_yeti_node(namespace, fur_name)
            yeti_node.Membership.set((',').join(tags))
        else:
            yeti_node = wizard_tools.get_node_from_name(node_name)
        yeti_node.File.set(file)


def sanity(stage_name, string_asset, exported_string_asset):
    ''' This function is triggered
        before the export and will stop the
        export process if the returned data is 
        "False"
        
        The "stage_name" argument is the name
        of the exported stage '''
    return True

def before_export(stage_name, string_asset, exported_string_asset):
    ''' This function is triggered
        before the export 

        The "stage_name" argument is the name
        of the exported stage

        You can return a list of objects 
        that wizard will add to the export '''
    return []

def after_export(stage_name, export_dir, string_asset, exported_string_asset):
    ''' This function is triggered
        after the export

        The "stage_name" argument is the name
        of the exported stage

        The "export_dir" argument is the path wher wizard exported the
        file as string '''
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
        to the current scene after the reference '''
    if referenced_stage_name == 'grooming':
        for file in os.listdir(referenced_files_dir):
            if file.endswith('.fur'):
                add_yeti_fur(namespace, referenced_stage_name, os.path.join(referenced_files_dir, file))