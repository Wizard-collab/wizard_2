# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_hooks
import wizard_communicate
from guerilla_render_wizard import wizard_tools

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

def reference_modeling(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'MODELING', 'modeling', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_modeling(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'MODELING', 'modeling', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def reference_grooming(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'GROOMING', 'grooming', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_grooming(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'GROOMING', 'grooming', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])
    
def reference_shading(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'SHADING', 'shading', reference_dic['string_variant'])

def update_shading(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'SHADING', 'shading', reference_dic['string_variant'])

def reference_custom(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'CUSTOM', 'custom', reference_dic['string_variant'])

def update_custom(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'CUSTOM', 'custom', reference_dic['string_variant'])

def reference_layout(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'LAYOUT', 'layout', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_layout(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'LAYOUT', 'layout', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def reference_animation(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'ANIMATION', 'animation', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_animation(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'ANIMATION', 'animation', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def reference_cfx(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'CFX', 'cfx', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_cfx(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'CFX', 'cfx', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def reference_fx(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'FX', 'fx', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_fx(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'FX', 'fx', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def reference_camera(reference_dic):
    import_file(reference_dic['namespace'], reference_dic['files'], 'CAMERA', 'camera', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def update_camera(reference_dic):
    update_file(reference_dic['namespace'], reference_dic['files'], 'CAMERA', 'camera', reference_dic['string_variant'])
    append_wizardTags_to_guerillaTags(reference_dic['namespace'])

def import_file(namespace, files_list, parent_GRP_name, stage_name, referenced_string_asset):
    old_objects = wizard_tools.get_all_nodes()
    if namespace not in wizard_tools.get_all_nodes():
        GRP = wizard_tools.add_GRP(parent_GRP_name)
        extension = files_list[0].split('.')[-1]
        if extension == 'abc' or  extension == 'gproject':
            create_ref(namespace, files_list, GRP)
        elif extension == 'vdb':
            create_vdb_ref(namespace, files_list, GRP)
        elif extension == 'gnode':
            merge(namespace, files_list, GRP)
        elif extension == 'fur':
            create_or_update_yeti_nodes(namespace, files_list, GRP)
        trigger_after_reference_hook(stage_name,
                                        files_list,
                                        namespace,
                                        wizard_tools.get_new_objects(old_objects),
                                        referenced_string_asset)

def update_file(namespace, files_list, parent_GRP_name, stage_name, referenced_string_asset):
    old_objects = wizard_tools.get_all_nodes()
    if namespace in wizard_tools.get_all_nodes():
        GRP = wizard_tools.add_GRP(parent_GRP_name)
        extension = files_list[0].split('.')[-1]
        if extension == 'abc' or  extension == 'gproject':
            update_ref(namespace, files_list, GRP)
        elif extension == 'vdb':
            update_vdb_ref(namespace, files_list, GRP)
        elif extension == 'gnode':
            update_merge(namespace, files_list, GRP)
        elif extension == 'fur':
            create_or_update_yeti_nodes(namespace, files_list, GRP)
        trigger_after_reference_hook(stage_name,
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects),
                                    referenced_string_asset)

def create_vdb_ref(namespace, files_list, GRP):
    sequence_files_list = wizard_tools.convert_files_list_to_sequence(files_list)
    with Modifier() as mod:
        refNode, topNodes = mod.createref(namespace, files_list[0], GRP)
    with Modifier() as mod:
        for primitive in topNodes:
            primitive.GeometryPath.set(sequence_files_list[0]+'@')
            tags = wizard_tools.get_tags_for_yeti_or_vdb_node(namespace, primitive.getname())
            primitive.Membership.set((',').join(tags))


def update_vdb_ref(namespace, files_list, GRP):
    sequence_files_list = wizard_tools.convert_files_list_to_sequence(files_list)
    refNode = wizard_tools.get_node_from_name(namespace)
    with Modifier() as mod:
        refNode.ReferenceFileName.set(files_list[0])
        refNode.reload(files_list[0])
        for node in wizard_tools.get_all_nodes(False):
            if node.belongstoreference(refNode):
                node.GeometryPath.set(sequence_files_list[0]+'@')

def create_ref(namespace, files_list, GRP):
    with Modifier() as mod:
        refNode, topNodes = mod.createref(namespace, files_list[0], GRP)

def update_ref(namespace, files_list, GRP):
    refNode = wizard_tools.get_node_from_name(namespace)
    with Modifier() as mod:
        refNode.ReferenceFileName.set(files_list[0])
        refNode.reload(files_list[0])

def merge(namespace, files_list, GRP):
    new_node = Document().loadfile(files_list[0])[0]
    new_node.move(GRP)
    new_node.rename(namespace)

def update_merge(namespace, files_list, GRP):
    if namespace in wizard_tools.get_all_nodes():
        wizard_tools.get_node_from_name(namespace).delete()
        merge(namespace, files_list, GRP)

def create_or_update_yeti_nodes(namespace, files_list, GRP):
    fur_nodes_files = wizard_tools.get_fur_nodes_files(files_list)
    for fur_node_file in fur_nodes_files:
        with Modifier() as mod:
            namespace_GRP = wizard_tools.add_GRP(namespace, GRP)
            fur_name = os.path.basename(fur_node_file).split('.')[-3]
            node_name = '{0}:{1}'.format(namespace, fur_name)
            if node_name not in wizard_tools.get_all_nodes():
                yeti_node = mod.createnode(node_name, "Yeti", namespace_GRP)
                yeti_node.HierarchyMode.set(2)
                tags = wizard_tools.get_tags_for_yeti_or_vdb_node(namespace, fur_name)
                yeti_node.Membership.set((',').join(tags))
            else:
                yeti_node = wizard_tools.get_node_from_name(node_name)
            yeti_node.File.set(fur_node_file)

def append_wizardTags_to_guerillaTags(namespace):
    refNode = wizard_tools.get_node_from_name(namespace)
    all_objects = wizard_tools.get_all_nodes(name=False)
    for node in all_objects:
        if node.belongstoreference(refNode):
            if node.hasAttr('wizardTags', 'Plug'):
                wizard_tags = node.wizardTags.get().split(',')
                guerilla_tags = node.Membership.get().split(',')
                tags_list = set(wizard_tags + guerilla_tags)
                if '' in tags_list:
                    tags_list.remove('')
                node.Membership.set((',').join(tags_list))

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects,
                                    referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('guerilla_render',
                                stage_name,
                                referenced_stage_name,
                                referenced_files_dir,
                                namespace,
                                new_objects,
                                string_asset,
                                referenced_string_asset)
    
