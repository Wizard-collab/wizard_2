# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_tools

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

# Hook modules
try:
    import guerilla_render_hook
except:
    guerilla_render_hook = None
    logger.error(str(traceback.format_exc()))
    logger.warning("Can't import guerilla_render_hook")

def reference_modeling(namespace, files_list):
    import_file(namespace, files_list, 'MODELING', 'modeling')
    append_wizardTags_to_guerillaTags(namespace)

def update_modeling(namespace, files_list):
    update_file(namespace, files_list, 'MODELING', 'modeling')
    append_wizardTags_to_guerillaTags(namespace)

def reference_shading(namespace, files_list):
    import_file(namespace, files_list, 'SHADING', 'shading')

def update_shading(namespace, files_list):
    update_file(namespace, files_list, 'SHADING', 'shading')

def reference_custom(namespace, files_list):
    import_file(namespace, files_list, 'CUSTOM', 'custom')

def update_custom(namespace, files_list):
    update_file(namespace, files_list, 'CUSTOM', 'custom')

def reference_layout(namespace, files_list):
    import_file(namespace, files_list, 'LAYOUT', 'layout')
    append_wizardTags_to_guerillaTags(namespace)

def update_layout(namespace, files_list):
    update_file(namespace, files_list, 'LAYOUT', 'layout')
    append_wizardTags_to_guerillaTags(namespace)

def reference_animation(namespace, files_list):
    import_file(namespace, files_list, 'ANIMATION', 'animation')
    append_wizardTags_to_guerillaTags(namespace)

def update_animation(namespace, files_list):
    update_file(namespace, files_list, 'ANIMATION', 'animation')
    append_wizardTags_to_guerillaTags(namespace)

def import_file(namespace, files_list, parent_GRP_name, stage_name):
    old_objects = wizard_tools.get_all_nodes()
    if namespace not in wizard_tools.get_all_nodes():
        GRP = wizard_tools.add_GRP(parent_GRP_name)
        extension = files_list[0].split('.')[-1]
        if extension == 'abc' or  extension == 'gproject':
            create_ref(namespace, files_list, GRP)
        elif extension == 'gnode':
            merge(namespace, files_list, GRP)
        trigger_after_reference_hook(stage_name,
                                        files_list,
                                        namespace,
                                        wizard_tools.get_new_objects(old_objects))

def update_file(namespace, files_list, parent_GRP_name, stage_name):
    old_objects = wizard_tools.get_all_nodes()
    if namespace in wizard_tools.get_all_nodes():
        GRP = wizard_tools.add_GRP(parent_GRP_name)
        extension = files_list[0].split('.')[-1]
        if extension == 'abc' or  extension == 'gproject':
            update_ref(namespace, files_list, GRP)
        elif extension == 'gnode':
            update_merge(namespace, files_list, GRP)
        trigger_after_reference_hook(stage_name,
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

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
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    # Trigger the after export hook
    if guerilla_render_hook:
        try:
            logger.info("Trigger after reference hook")
            guerilla_render_hook.after_reference(stage_name,
                                        referenced_stage_name,
                                        referenced_files_dir,
                                        namespace,
                                        new_objects)
        except:
            logger.info("Can't trigger after reference hook")
            logger.error(str(traceback.format_exc()))
