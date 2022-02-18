# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

def get_all_nodes():
    nodes_list = []
    for node in Document().children(recursive=True):
        nodes_list.append(node.getname())
    return nodes_list

def add_GRP(grp_name, parent = None):
    if grp_name not in get_all_nodes():
        with Modifier() as mod:
            if parent:
                mod.createnode(grp_name, parent=parent)
            else:
                mod.createnode(grp_name)
    node = get_node_from_name(grp_name)
    return node

def get_node_from_name(name):
    nodes_list = []
    for node in Document().children(recursive=True):
        if node.getname() == name:
            break
    return node
