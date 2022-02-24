# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from guerilla_render_wizard import wizard_tools

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

def reference_modeling(namespace, files_list):
    import_file(namespace, files_list, 'MODELING')

def update_modeling(namespace, files_list):
    update_file(namespace, files_list, 'MODELING')

def reference_shading(namespace, files_list):
    import_file(namespace, files_list, 'SHADING')

def update_shading(namespace, files_list):
    update_file(namespace, files_list, 'SHADING')

def reference_custom(namespace, files_list):
    import_file(namespace, files_list, 'CUSTOM')

def update_custom(namespace, files_list):
    update_file(namespace, files_list, 'CUSTOM')

def import_file(namespace, files_list, parent_GRP_name):
    if namespace not in wizard_tools.get_all_nodes():
        GRP = wizard_tools.add_GRP(parent_GRP_name)
        extension = files_list[0].split('.')[-1]
        if extension == 'abc' or  extension == 'gproject':
            create_ref(namespace, files_list, GRP)
        elif extension == 'gnode':
            merge(namespace, files_list, GRP)

def update_file(namespace, files_list, parent_GRP_name):
    if namespace in wizard_tools.get_all_nodes():
        GRP = wizard_tools.add_GRP(parent_GRP_name)
        extension = files_list[0].split('.')[-1]
        if extension == 'abc' or  extension == 'gproject':
            update_ref(namespace, files_list, GRP)
        elif extension == 'gnode':
            update_merge(namespace, files_list, GRP)

def create_ref(namespace, files_list, GRP):
    with Modifier() as mod:
        refNode, topNodes = mod.createref(namespace, files_list[0], GRP)

def merge(namespace, files_list, GRP):
    new_node = Document().loadfile(files_list[0])[0]
    new_node.move(GRP)
    new_node.rename(namespace)

def update_merge(namespace, files_list, GRP):
    if namespace in wizard_tools.get_all_nodes():
        wizard_tools.get_node_from_name(namespace).delete()
        merge(namespace, files_list, GRP)

def update_ref(namespace, files_list, GRP):
    refNode = wizard_tools.get_node_from_name(namespace)
    with Modifier() as mod:
        refNode.ReferenceFileName.set(files_list[0])
        refNode.reload(files_list[0])
