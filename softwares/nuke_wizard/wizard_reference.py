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
from nuke_wizard import wizard_tools

# Nuke modules
import nuke

def reference_custom(namespace, files_list):
    import_from_extension(namespace, files_list, 'custom')

def update_custom(namespace, files_list):
    update_from_extension(namespace, files_list, 'custom')

def reference_camera(namespace, files_list):
    import_from_extension(namespace, files_list, 'camera')

def update_camera(namespace, files_list):
    update_from_extension(namespace, files_list, 'camera')

def reference_lighting(namespace, files_list):
    import_from_extension(namespace, files_list, 'lighting')

def update_lighting(namespace, files_list):
    update_from_extension(namespace, files_list, 'lighting')

def import_from_extension(namespace, files_list, stage_name):
    old_nodes = wizard_tools.get_all_nodes()
    extension = files_list[0].split('.')[-1]
    if extension == 'exr':
        reference_exr(namespace, files_list)
    elif extension == 'nk':
        import_nk(namespace, files_list)
    elif extension == 'abc':
        if stage_name == 'camera':
            reference_abc_camera(namespace, files_list)
    trigger_after_reference_hook(stage_name,
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_nodes))

def update_from_extension(namespace, files_list, stage_name):
    old_nodes = wizard_tools.get_all_nodes()
    extension = files_list[0].split('.')[-1]
    if extension == 'exr':
        update_exr(namespace, files_list)
    elif extension == 'nk':
        update_nk(namespace, files_list)
    elif extension == 'abc':
        if stage_name == 'camera':
            update_abc_camera(namespace, files_list)
    trigger_after_reference_hook(stage_name,
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_nodes))

def import_nk(namespace, files_list):
    if namespace not in wizard_tools.get_all_namespaces().keys():
        if len(files_list) == 1:
            old_nodes = wizard_tools.get_all_nodes()
            nuke.scriptSource(files_list[0])
            new_nodes = wizard_tools.get_new_objects(old_nodes)
            wizard_tools.backdrop_nodes(new_nodes, namespace, namespace_knob = True)
        else:
            logger.warning("Can't merge multiple files")

def update_nk(namespace, files_list):
    if namespace in wizard_tools.get_all_namespaces().keys():
        logger.info(f"Can't update {namespace} since it is merged")

def reference_abc_camera(namespace, files_list):
    if namespace not in wizard_tools.get_all_namespaces().keys():
        if len(files_list) == 1:
            old_nodes = wizard_tools.get_all_nodes()
            camera_node = nuke.createNode('Camera3')
            camera_node['name'].setValue(namespace+'_CAMERA')
            camera_node['read_from_file_link'].setValue(True)
            camera_node['file_link'].setValue(files_list[0])
            wizard_tools.add_namespace_knob(camera_node, namespace)
            new_nodes = wizard_tools.get_new_objects(old_nodes)
            wizard_tools.backdrop_nodes(new_nodes, namespace)
        else:
            logger.warning("Can't merge multiple files")

def update_abc_camera(namespace, files_list):
    if namespace in wizard_tools.get_all_namespaces().keys():
        if len(files_list) == 1:
            camera_node = wizard_tools.get_all_namespaces()[namespace][0]
            camera_node['file_link'].setValue(files_list[0])
        else:
            logger.warning("Can't merge multiple files")

def reference_exr(namespace, files_list):
    if namespace not in wizard_tools.get_all_namespaces().keys():
        paths_dic = wizard_tools.exr_list_to_paths_list(files_list)
        reads_list = []
        for path in paths_dic.keys():
            read_name = os.path.basename(path).split('.')[0]
            frange = paths_dic[path]
            read = wizard_tools.create_read(read_name, namespace)
            wizard_tools.set_read_data(read, path, frange)
            reads_list.append(read)
        wizard_tools.align_nodes(reads_list)
        wizard_tools.backdrop_nodes(reads_list, namespace)

def update_exr(namespace, files_list):
    all_namespaces = wizard_tools.get_all_namespaces()
    if namespace in all_namespaces.keys():
        existing_reads_list = all_namespaces[namespace]
        existing_read_names_dic = dict()
        for read in existing_reads_list:
            read_name = read['name'].value()
            existing_read_names_dic[read_name] = read
        paths_dic = wizard_tools.exr_list_to_paths_list(files_list)
        reads_list = []
        for path in paths_dic.keys():
            read_name = os.path.basename(path).split('.')[0]
            frange = paths_dic[path]
            if read_name in existing_read_names_dic.keys():
                read = existing_read_names_dic[read_name]
            else:
                read = wizard_tools.create_read(read_name, namespace)
            wizard_tools.set_read_data(read, path, frange)
            reads_list.append(read)
        for read in existing_reads_list:
            if read not in reads_list:
                nuke.delete(read)
        wizard_tools.align_nodes(reads_list)
        wizard_tools.backdrop_nodes(reads_list, namespace)

def trigger_after_reference_hook(referenced_stage_name,
                                    files_list,
                                    namespace,
                                    new_objects):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = wizard_tools.get_file_dir(files_list[0])
    wizard_hooks.after_reference_hooks('nuke',
                                stage_name,
                                referenced_stage_name,
                                referenced_files_dir,
                                namespace,
                                new_objects)