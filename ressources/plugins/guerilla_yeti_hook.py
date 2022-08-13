# coding: utf-8
# Wizard plugin hook

import os

import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_tools

# Guerilla render modules
from guerilla import Document, Modifier, pynode, Node, Plug

def yeti_after_reference(stage_name, 
                        referenced_stage_name, 
                        referenced_files_dir,
                        namespace, 
                         new_objects):
    if referenced_stage_name == 'grooming':
        for file in os.listdir(referenced_files_dir):
            if file.endswith('.fur'):
                add_yeti_fur(namespace, referenced_stage_name, os.path.join(referenced_files_dir, file))

def add_yeti_fur(namespace, referenced_stage_name, file):
    GRP = wizard_tools.add_GRP(referenced_stage_name.upper())
    with Modifier() as mod:
        namespace_GRP = wizard_tools.add_GRP(namespace, GRP)
        fur_name = os.path.basename(file).split('.fur')[0]
        node_name = '{0}:{1}'.format(namespace, fur_name)
        if node_name not in wizard_tools.get_all_nodes():
        	yeti_node = mod.createnode(node_name, "Yeti", namespace_GRP)
        	yeti_node.HierarchyMode.set(2)
        	yeti_node.Membership.set(fur_name)
    	else:
    		yeti_node = wizard_tools.get_node_from_name(node_name)
        yeti_node.File.set(file)

