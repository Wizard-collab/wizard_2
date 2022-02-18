# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from guerilla_render_wizard import wizard_tools

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

def reference_modeling(namespace, files_list):
    if namespace not in wizard_tools.get_all_nodes():
        with Modifier() as mod:
            geo_GRP = wizard_tools.add_GRP('MODELING')
            refNode, topNodes = mod.createref(namespace, files_list[0], geo_GRP)

def update_modeling(namespace, files_list):
    if namespace in wizard_tools.get_all_nodes():
        refNode = wizard_tools.get_node_from_name(namespace)
        refNode.ReferenceFileName.set(files_list[0])