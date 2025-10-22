# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Wizard modules
import wizard_communicate
import wizard_hooks

# Substance Painter modules
import substance_painter.logging as logging
import substance_painter.resource


def get_mesh_file():
    references = wizard_communicate.get_references(
        int(os.environ['wizard_work_env_id']))
    if 'modeling' not in references.keys():
        logging.error("No modeling references found")
        return
    if len(references['modeling']) != 1:
        logging.error("Please reference only ONE modeling export")
        return
    
    files_list = references['modeling'][0]['files']
    abc_files = []

    for file in files_list:
        if not file.endswith('.abc'):
            continue
        abc_files.append(file)

    mesh_file_path = abc_files[0]
    return mesh_file_path


def import_texturing(reference_dic):
    import_from_extension(
        reference_dic['namespace'], reference_dic['files'], 'custom', reference_dic['string_stage'])


def import_from_extension(namespace, files_list, stage_name, referenced_string_asset):
    extension = files_list[0].split('.')[-1]
    if extension == 'sbsar':
        reference_sbsar(namespace, files_list)
    trigger_after_reference_hook(stage_name,
                                 files_list,
                                 namespace,
                                 [],
                                 referenced_string_asset)


def reference_sbsar(namespace, files_list):
    new_resource = substance_painter.resource.import_project_resource(
        files_list[0],
        substance_painter.resource.Usage.BASE_MATERIAL)


def trigger_after_reference_hook(referenced_stage_name,
                                 files_list,
                                 namespace,
                                 new_objects,
                                 referenced_string_asset):
    stage_name = os.environ['wizard_stage_name']
    referenced_files_dir = os.path.dirname(files_list[0])
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_reference_hooks('substance_designer',
                                       stage_name,
                                       referenced_stage_name,
                                       referenced_files_dir,
                                       namespace,
                                       new_objects,
                                       string_asset,
                                       referenced_string_asset)
