# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This module is the main instances management module
# You can create, get the path and archive the following instances
#/domains
#/categories
#/assets
#/stages
#/variants
#/work env
#/versions
#/export assets
#/export versions

# The creation of an instance basically log the instance 
# in the project database and create the corresponding folders
# on the file system

# The archiving of an instance basically archive the corresponding 
# folder, delete the original folder from the file
# system and remove the instance from the project database

# The path query of an instance will only access the database and
# construct the directory name, this modules doesn't
# query the file system

# Python modules
import os
import time
import shutil
import json
import logging

# Wizard modules
from wizard.core import environment
from wizard.core import events
from wizard.core import project
from wizard.core import site
from wizard.core import tools
from wizard.core import image
from wizard.core import game
from wizard.core import asset_tracking
from wizard.vars import assets_vars
from wizard.vars import softwares_vars

logger = logging.getLogger(__name__)

def create_domain(name):
    domain_id = None
    if tools.is_safe(name):
        dir_name = os.path.normpath(os.path.join(environment.get_project_path(),
                                    name))
        domain_id = project.add_domain(name)
        if domain_id:
            if not tools.create_folder(dir_name):
                project.remove_domain(domain_id)
                domain_id = None
    else:
        logger.warning(f"{name} contains illegal characters")
    return domain_id

def archive_domain(domain_id):
    if site.is_admin():
        domain_row = project.get_domain_data(domain_id)
        if domain_row:
            dir_name = get_domain_path(domain_id)
            if os.path.isdir(dir_name):
                if tools.make_archive(dir_name):
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
            else:
                logger.warning(f"{dir_name} not found")
            return project.remove_domain(domain_id)
        else:
            return None
    else:
        return None

def create_category(name, domain_id):
    category_id = None
    if tools.is_safe(name):
        domain_path = get_domain_path(domain_id)
        if domain_path:
            dir_name = os.path.normpath(os.path.join(domain_path, name))
            category_id = project.add_category(name, domain_id)
            if category_id:
                if not tools.create_folder(dir_name):
                    project.remove_category(category_id)
                    category_id = None
                else:
                    events.add_creation_event('category', category_id)
                    game.add_xps(2)
        else:
            logger.error("Can't create category")
    else:
        logger.warning(f"{name} contains illegal characters")
    return category_id

def archive_category(category_id):
    if site.is_admin():
        category_row = project.get_category_data(category_id)
        if category_row:
            dir_name = get_category_path(category_id)
            if os.path.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
            else:
                logger.warning(f"{dir_name} not found")
                archive_file = ''
            success = project.remove_category(category_id)
            if success:
                events.add_archive_event(f"Archived {instance_to_string(('domain', category_row['domain_id']))}/{category_row['name']}",
                                                archive_file)
            return success
        else:
            return None
    else:
        return None

def create_asset(name, category_id, inframe=100, outframe=220, preroll=0, postroll=0):
    asset_id = None
    if tools.is_safe(name):
        category_path = get_category_path(category_id)
        if category_path:
            dir_name = os.path.normpath(os.path.join(category_path, name))
            asset_id = project.add_asset(name, category_id, inframe, outframe, preroll, postroll)
            if asset_id:
                if not tools.create_folder(dir_name):
                    project.remove_asset(asset_id)
                    asset_id = None
                else:
                    events.add_creation_event('asset', asset_id)
                    game.add_xps(2)
        else:
            logger.error("Can't create asset")
    else:
        logger.warning(f"{name} contains illegal characters")
    return asset_id

def archive_asset(asset_id):
    if site.is_admin():
        asset_row = project.get_asset_data(asset_id)
        if asset_row:
            dir_name = get_asset_path(asset_id)
            if os.path.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
                    
            else:
                logger.warning(f"{dir_name} not found")
                archive_file = ''
            success = project.remove_asset(asset_id)
            if success:
                events.add_archive_event(f"Archived {instance_to_string(('category', asset_row['category_id']))}/{asset_row['name']}",
                                                archive_file)
            return success
        else:
            return None
    else:
        return None

def get_asset_data_from_work_env_id(work_env_id):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    asset_id = project.get_stage_data(stage_id, 'asset_id')
    if asset_id:
        asset_row = project.get_asset_data(asset_id)
        return asset_row
    else:
        return None

def create_stage(name, asset_id):
    # The stage creation need to follow some name rules
    # if category is assets, the rules are :
    #    modeling
    #    rigging
    #    grooming
    #    texturing
    #    shading

    category_id = project.get_asset_data(asset_id, 'category_id')
    category_name = project.get_category_data(category_id, 'name')
    domain_id = project.get_category_data(category_id, 'domain_id')
    domain_name = project.get_domain_data(domain_id, 'name')

    allowed = None

    if domain_name == assets_vars._assets_:
        if name in assets_vars._assets_stages_list_:
            allowed = 1
    if domain_name == assets_vars._sequences_:
        if name in assets_vars._sequences_stages_list_:
            allowed = 1
    if domain_name == assets_vars._library_:
        if name in assets_vars._library_stages_list_:
            allowed = 1

    if allowed:
        asset_path = get_asset_path(asset_id)
        if asset_path:
            dir_name = os.path.normpath(os.path.join(asset_path, name))
            stage_id = project.add_stage(name, asset_id)
            if stage_id:
                if not tools.create_folder(dir_name):
                    project.remove_stage(stage_id)
                    stage_id = None
                else:
                    variant_id = create_variant('main', stage_id, 'default variant')
                    if variant_id:
                        project.set_stage_default_variant(stage_id, variant_id)
            return stage_id
        else:
            logger.error("Can't create stage")
            return None
    else:
        logger.warning(f"{name} doesn't match stages rules")
        return None

def archive_stage(stage_id):
    if site.is_admin():
        stage_row = project.get_stage_data(stage_id)
        if stage_row:
            dir_name = get_stage_path(stage_id)
            if os.path.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
            else:
                logger.warning(f"{dir_name} not found")
                archive_file = ''
            success = project.remove_stage(stage_id)
            if success:
                events.add_archive_event(f"Archived {instance_to_string(('asset', stage_row['asset_id']))}/{stage_row['name']}", archive_file)
            return success
        else:
            return None
    else:
        return None

def create_variant(name, stage_id, comment=''):
    variant_id = None
    if tools.is_safe(name):
        stage_path = get_stage_path(stage_id)
        if stage_path:
            dir_name = os.path.normpath(os.path.join(stage_path, name))
            variant_id = project.add_variant(name, stage_id, comment)
            if variant_id:
                if not tools.create_folder(dir_name):
                    project.remove_variant(variant_id)
                    variant_id = None
                else:
                    # Add other folders
                    tools.create_folder(os.path.normpath(os.path.join(dir_name, '_EXPORTS')))
                    tools.create_folder(os.path.normpath(os.path.join(dir_name, '_SANDBOX')))
                    events.add_creation_event('variant', variant_id)
                    game.add_xps(2)
        else:
            logger.error("Can't create variant")
    else:
        logger.warning(f"{name} contains illegal characters")
    return variant_id

def archive_variant(variant_id):
    if site.is_admin():
        variant_row = project.get_variant_data(variant_id)
        if variant_row:
            dir_name = get_variant_path(variant_id)
            if os.path.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
            else:
                logger.warning(f"{dir_name} not found")
                archive_file=''
            success = project.remove_variant(variant_id)
            if success:
                events.add_archive_event(f"Archived {instance_to_string(('stage', variant_row['stage_id']))}/{variant_row['name']}",
                                                archive_file)
            return success
        else:
            return None
    else:
        return None

def modify_variant_state(variant_id, state, comment=''):
    project.set_variant_data(variant_id, 'state', state)
    if comment is not None and comment != '':
        project.set_variant_data(variant_id, 'tracking_comment', comment)
    asset_tracking.add_state_switch_event(variant_id, state, comment)

def add_variant_comment(variant_id, comment):
    project.set_variant_data(variant_id, 'tracking_comment', comment)
    asset_tracking.add_comment_event(variant_id, comment)

def modify_variant_assignment(variant_id, user_name):
    project.set_variant_data(variant_id, 'assignment', user_name)
    asset_tracking.add_assignment_event(variant_id, user_name)

def modify_variant_estimation(variant_id, seconds):
    project.set_variant_data(variant_id, 'estimated_time', seconds)
    asset_tracking.add_estimation_event(variant_id, seconds)

def add_work_time(work_env_id, work_time):
    project.add_work_time(work_env_id, work_time)
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    project.add_variant_work_time(variant_id, work_time)
    asset_tracking.add_work_session_event(variant_id, work_time)

def get_software_id_by_name(software):
    return project.get_software_data_by_name(software, 'id')

def create_work_env(software_id, variant_id):
    work_env_id = None
    name = project.get_software_data(software_id, 'name')
    if name in project.get_softwares_names_list():
        variant_path = get_variant_path(variant_id)
        if variant_path:
            stage_row = project.get_stage_data(project.get_variant_data(variant_id, 'stage_id'))
            if stage_row['name'] == assets_vars._custom_stage_:
                export_extension = assets_vars._ext_dic_[assets_vars._custom_stage_][name][0]
            else:
                export_extension = None
            dir_name = os.path.normpath(os.path.join(variant_path, name))
            screenshots_dir_name = os.path.normpath(os.path.join(dir_name, 'screenshots'))
            work_env_id = project.add_work_env(name,
                                                software_id,
                                                variant_id,
                                                export_extension)
            if work_env_id:
                if (not tools.create_folder(dir_name)) or (not tools.create_folder(screenshots_dir_name)) :
                    project.remove_work_env(work_env_id)
                    work_env_id = None
                else:
                    add_version(work_env_id, do_screenshot=0, fresh=1)
        else:
            logger.error("Can't create work env")
    else:
        logger.warning(f"{name} is not a valid work environment ( software not handled )")
    return work_env_id

def create_references_from_variant_id(work_env_id, variant_id):
    export_rows = project.get_variant_export_childs(variant_id)
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    stage = project.get_stage_data(stage_id, 'name')
    if export_rows is not None:
        if stage == assets_vars._modeling_:
            export_rows = [export_rows[0]]
        for export_row in export_rows:
            export_version_id = project.get_last_export_version(export_row['id'], 'id')
            if export_version_id is not None and len(export_version_id)>=1:
                create_reference(work_env_id, export_version_id[0])
        return 1
    else:
        return None

def create_reference(work_env_id, export_version_id):
    namespaces_list = project.get_references(work_env_id, 'namespace')
    count = 0
    namespace_raw = build_namespace(export_version_id)
    namespace = f"{namespace_raw}_{str(count).zfill(4)}"
    while namespace in namespaces_list:
        count+=1
        namespace = f"{namespace_raw}_{str(count).zfill(4)}"
    return project.create_reference(work_env_id,
                                            export_version_id,
                                            namespace)

def remove_reference(reference_id):
    return project.remove_reference(reference_id)

def set_reference_last_version(reference_id):
    export_version_id = project.get_reference_data(reference_id, 'export_version_id')
    if export_version_id is not None:
        export_version_row = project.get_export_version_data(export_version_id)
        export_row = project.get_export_data(export_version_row['export_id'])
        last_export_version_id = project.get_last_export_version(export_row['id'], 'id')
        if last_export_version_id is not None and len(last_export_version_id)==1:
            if last_export_version_id[0] != export_version_id:
                project.update_reference(reference_id, last_export_version_id[0])
                return 1
            else:
                logger.info("Reference is up to date")
                return None

def modify_modeling_reference_LOD(work_env_id, LOD, namespaces_list):
    references_rows = project.get_references(work_env_id)
    print(namespaces_list)
    for reference_row in references_rows:
        if (reference_row['stage'] == assets_vars._modeling_) and (reference_row['namespace'] in namespaces_list):
            export_row = project.get_export_data(reference_row['export_id'])
            export_rows = project.get_variant_export_childs(export_row['variant_id'])
            for export_row in export_rows:
                if export_row['name'] == LOD:
                    project.modify_reference_export(reference_row['id'], export_row['id'])

def get_references_files(work_env_id):
    references_rows = project.get_references(work_env_id)
    references_dic = dict()
    for reference_row in references_rows:
        reference_files_list = json.loads(project.get_export_version_data(reference_row['export_version_id'], 'files'))

        variant_id = project.get_work_env_data(reference_row['work_env_id'], 'variant_id')
        stage_id = project.get_variant_data(variant_id, 'stage_id')
        asset_id = project.get_stage_data(stage_id, 'asset_id')
        asset_name = project.get_asset_data(asset_id, 'name')

        reference_dic = dict()
        reference_dic['files'] = reference_files_list
        reference_dic['namespace'] = reference_row['namespace']
        reference_dic['asset_name'] = asset_name
        if reference_row['stage'] not in references_dic.keys():
            references_dic[reference_row['stage']] = []
        references_dic[reference_row['stage']].append(reference_dic)
    return references_dic

def merge_file_as_export_version(export_name, files, variant_id, comment='', execute_xp=True):
    return add_export_version(export_name, files, variant_id, None, comment)

def add_export_version_from_version_id(export_name, files, version_id, comment='', execute_xp=True):
    work_env_row = project.get_work_env_data(project.get_version_data(version_id, 'work_env_id'))
    if work_env_row is not None:
        variant_id = work_env_row['variant_id']
        return add_export_version(export_name, files, variant_id, version_id, comment, execute_xp)

def add_export_version(export_name, files, variant_id, version_id, comment='', execute_xp=True):
    # For adding an export version, wizard need an existing files list
    # it will just create the new version in the database
    # and copy the files in the corresponding directory

    variant_row = project.get_variant_data(variant_id)
    stage_name = project.get_stage_data(variant_row['stage_id'], 'name')
    extension_errors = []

    # Get the extensions rules of the stage
    extensions_rules = []
    for software in assets_vars._ext_dic_[stage_name].keys():
        extensions_rules += assets_vars._ext_dic_[stage_name][software]
    extensions_rules = list(dict.fromkeys(extensions_rules))

    for file in files:
        if os.path.splitext(file)[-1].replace('.', '') not in extensions_rules:
            extension_errors.append(file)
    if extension_errors == []:
        if variant_row:
            export_id = get_or_add_export(export_name, variant_id)
            if export_id:
                last_version_list = project.get_last_export_version(export_id, 'name')
                if last_version_list is not None and len(last_version_list) == 1:
                    last_version = last_version_list[0]
                    new_version =  str(int(last_version)+1).zfill(4)
                else:
                    new_version = '0001'
                export_path = get_export_path(export_id)
                if export_path:
                    dir_name = os.path.normpath(os.path.join(export_path, new_version))
                    if not tools.create_folder(dir_name):
                        project.remove_export_version(export_version_id)
                        export_version_id = None
                    else:
                        copied_files = tools.copy_files(files, dir_name)
                        if not copied_files:
                            if not tools.remove_folder(dir_name):
                                logger.warning(f"{dir_name} can't be removed, keep export version {new_version} in database")
                            export_version_id = None
                        else:
                            export_version_id = project.add_export_version(new_version,
                                                                            copied_files,
                                                                            export_id,
                                                                            version_id,
                                                                            comment)
                            if execute_xp:
                                game.add_xps(3)
                                game.analyse_comment(comment, 10)
                            events.add_export_event(export_version_id)
                return export_version_id
            else:
                return None
        else:
            return None
    else:
        for file in extension_errors:
            logger.warning(f"{file} format doesn't math the stage export rules ( {(', ').join(extensions_rules)} )")

def request_export(work_env_id, export_name, multiple=None, only_dir=None):
    # Gives a temporary ( and local ) export file name
    # for the softwares
    dir_name = tools.temp_dir()
    logger.info(f"Temporary directory created : {dir_name}, if something goes wrong in the export please go there to find your temporary export file")
    file_name = build_export_file_name(work_env_id, export_name, multiple)
    if file_name and not only_dir:
        return os.path.normpath(os.path.join(dir_name, file_name))
    elif file_name and only_dir:
        return dir_name
    else:
        return None

def archive_export(export_id):
    if site.is_admin():
        export_row = project.get_export_data(export_id)
        if export_row:
            dir_name = get_export_path(export_id)
            if os.path.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
            else:
                logger.warning(f"{dir_name} not found")
                archive_file = ''
            success = project.remove_export(export_id)
            if success:
                events.add_archive_event(f"Archived {instance_to_string(('variant', export_row['variant_id']))}/{export_row['name']}",
                                                archive_file)
            return success
        else:
            return None
    else:
        return None

def get_or_add_export(name, variant_id):
    # If the given export name exists, it return
    # the corresponding export_id
    # If i doesn't exists, it add it to the database
    # and rreturn the new export_id
    export_id = None
    if tools.is_safe(name):
        variant_path = get_variant_path(variant_id)
        if variant_path:
            dir_name = os.path.normpath(os.path.join(variant_path, '_EXPORTS', name))
            is_export = project.is_export(name, variant_id)
            if not is_export:
                export_id = project.add_export(name, variant_id)
                if not tools.create_folder(dir_name):
                    project.remove_export(export_id)
                    export_id = None
            else:
                export_id = project.get_export_by_name(name, variant_id)['id']
        else:
            logger.error("Can't create export")
    else:
        logger.warning(f"{name} contains illegal characters")
    return export_id

def archive_export_version(export_version_id):
    if site.is_admin():
        export_version_row = project.get_export_version_data(export_version_id)
        export_id = export_version_row['export_id']
        if export_version_row:
            dir_name = get_export_version_path(export_version_id)
            if os.path.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    shutil.rmtree(dir_name)
                    logger.info(f"{dir_name} deleted")
            else:
                logger.warning(f"{dir_name} not found")
                archive_file = ''
            success = project.remove_export_version(export_version_id)
            if success:
                events.add_archive_event(f"Archived{instance_to_string(('export', export_version_row['export_id']))}/{export_version_row['name']}",
                                                archive_file)
                if len(project.get_export_versions(export_id)) == 0:
                    archive_export(export_id)
            return success
        else:
            return None
    else:
        return None

def add_version(work_env_id, comment="", do_screenshot=1, fresh=None, analyse_comment=None):
    if fresh:
        new_version = '0001'
    else:
        last_version_list = project.get_last_work_version(work_env_id, 'name')
        if len(last_version_list) == 1:
            last_version = last_version_list[0]
            new_version =  str(int(last_version)+1).zfill(4)
        else:
            new_version = '0001'

    dirname = get_work_env_path(work_env_id)
    screenshot_dir_name = os.path.join(dirname, 'screenshots')

    file_name = os.path.normpath(os.path.join(dirname, 
                            build_version_file_name(work_env_id, new_version)))
    file_name_ext = os.path.splitext(file_name)[-1]

    basename = os.path.basename(file_name)
    screenshot_file = os.path.join(screenshot_dir_name, 
                    basename.replace(file_name_ext, '.jpg'))
    thumbnail_file = os.path.join(screenshot_dir_name, 
                    basename.replace(file_name_ext, '.thumbnail.jpg'))


    if do_screenshot:
        screenshot_file, thumbnail_file = image.screenshot(screenshot_file, thumbnail_file)
        variant_id = project.get_work_env_data(work_env_id, 'variant_id')
        stage_id = project.get_variant_data(variant_id, 'stage_id')
        asset_id = project.get_stage_data(stage_id, 'asset_id')
        project.modify_asset_preview(asset_id, thumbnail_file)

    version_id = project.add_version(new_version,
                                                file_name,
                                                work_env_id,
                                                comment,
                                                screenshot_file,
                                                thumbnail_file)
    if (analyse_comment or fresh) and version_id:
        game.add_xps(1)
        game.analyse_comment(comment, 2)
    return version_id

def set_asset_preview(asset_id, image_file):
    if image_file is not None:
        preview_path = os.path.join(get_asset_path(asset_id), 'preview')
        if not os.path.isdir(preview_path):
            os.mkdir(preview_path)
        destination = os.path.join(preview_path, f"{project.get_asset_data(asset_id, 'name')}.jpg")
        preview_file = image.resize_preview(image_file, destination)
    else:
        preview_file = None
    project.modify_asset_manual_preview(asset_id, preview_file)

def merge_file(file, work_env_id, comment="", do_screenshot=1):
    if os.path.isfile(file):
        software_extension = project.get_software_data(project.get_work_env_data(work_env_id, 'software_id'), 'extension')
        file_extension = os.path.splitext(file)[-1].replace('.', '')
        if software_extension == file_extension:
            version_id = add_version(work_env_id, comment, do_screenshot)
            version_row = project.get_version_data(version_id)
            shutil.copyfile(file, version_row['file_path'])
            logger.info(f"{file} merged in new version {version_row['name']}")
            return version_id
        else:
            logger.warning(f"{file} doesn't match the work environment extension rules ( .ma )")
            return None
    else:
        logger.warning(f"{file} doesn't exists")
        return None

def duplicate_version(version_id, comment=None):
    new_version_id = None
    version_row = project.get_version_data(version_id)
    if version_row is not None:
        if comment is None:
            comment = version_row['comment']
        new_version_id = merge_file(version_row['file_path'],
                                    version_row['work_env_id'],
                                    comment, 0)
        new_version_row = project.get_version_data(new_version_id)
        if os.path.isfile(version_row['screenshot_path']):
            shutil.copyfile(version_row['screenshot_path'], new_version_row['screenshot_path'])
        if os.path.isfile(version_row['thumbnail_path']):
            shutil.copyfile(version_row['thumbnail_path'], new_version_row['thumbnail_path'])
    return new_version_id

def archive_version(version_id):
    if site.is_admin():
        version_row = project.get_version_data(version_id)
        if version_row['name'] != '0001':
            if version_row:
                if os.path.isfile(version_row['file_path']):
                    zip_file = os.path.join(os.path.split(version_row['file_path'])[0], 
                                'archives.zip')
                    if tools.zip_files([version_row['file_path']], zip_file):
                        os.remove(version_row['file_path'])
                        logger.info(f"{version_row['file_path']} deleted")
                else:
                    logger.warning(f"{version_row['file_path']} not found")
                success = project.remove_version(version_row['id'])
                return success
            else:
                return None    
        else:
            logger.warning("You can't archive the default version (0001)")
            return None    
    else:
        return None

def create_group(name, auto_update=False, color='#798fe8'):
    return project.create_group(name, auto_update, color)

def remove_group(group_id):
    return project.remove_group(group_id)

def create_referenced_group(work_env_id, group_id):
    namespaces_list = project.get_referenced_groups(work_env_id, 'namespace')
    count = 0
    namespace_raw = project.get_group_data(group_id, 'name')
    namespace = f"{namespace_raw}_{str(count).zfill(1)}"
    while namespace in namespaces_list:
        count+=1
        namespace = f"{namespace_raw}_{str(count).zfill(1)}"
    return project.create_referenced_group(work_env_id,
                                            group_id,
                                            namespace)

def remove_referenced_group(referenced_group_id):
    return project.remove_referenced_group(referenced_group_id)

def create_grouped_references_from_variant_id(group_id, variant_id):
    export_rows = project.get_variant_export_childs(variant_id)
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    stage = project.get_stage_data(stage_id, 'name')
    if export_rows is not None:
        if stage == assets_vars._modeling_:
            export_rows = [export_rows[0]]
        for export_row in export_rows:
            export_version_id = project.get_last_export_version(export_row['id'], 'id')
            if export_version_id is not None and len(export_version_id)>=1:
                create_grouped_reference(group_id, export_version_id[0])
        return 1
    else:
        return None

def create_grouped_reference(group_id, export_version_id):
    namespaces_list = project.get_grouped_references(group_id, 'namespace')
    count = 0
    namespace_raw = build_namespace(export_version_id)
    namespace = f"{namespace_raw}_{str(count).zfill(4)}"
    while namespace in namespaces_list:
        count+=1
        namespace = f"{namespace_raw}_{str(count).zfill(4)}"
    return project.create_grouped_reference(group_id,
                                            export_version_id,
                                            namespace)

def remove_grouped_reference(grouped_reference_id):
    return project.remove_grouped_reference(grouped_reference_id)

def set_grouped_reference_last_version(grouped_reference_id):
    export_version_id = project.get_grouped_reference_data(grouped_reference_id, 'export_version_id')
    if export_version_id is not None:
        export_version_row = project.get_export_version_data(export_version_id)
        export_row = project.get_export_data(export_version_row['export_id'])
        last_export_version_id = project.get_last_export_version(export_row['id'], 'id')
        if last_export_version_id is not None and len(last_export_version_id)==1:
            if last_export_version_id[0] != export_version_id:
                project.update_grouped_reference(grouped_reference_id, last_export_version_id[0])
                return 1
            else:
                logger.info("Grouped reference is up to date")
                return None

def get_domain_path(domain_id):
    dir_name = None
    domain_name = project.get_domain_data(domain_id, 'name')
    if domain_name:
        dir_name = os.path.join(environment.get_project_path(), domain_name)
    return dir_name

def get_category_path(category_id):
    dir_name = None
    category_row = project.get_category_data(category_id)
    if category_row:
        category_name = category_row['name']
        domain_path = get_domain_path(category_row['domain_id'])
        if category_name and domain_path:
            dir_name = os.path.join(domain_path, category_name)
    return dir_name

def get_asset_path(asset_id):
    dir_name = None
    asset_row = project.get_asset_data(asset_id)
    if asset_row:
        asset_name = asset_row['name']
        category_path = get_category_path(asset_row['category_id'])
        if asset_name and category_path:
            dir_name = os.path.join(category_path, asset_name)
    return dir_name

def get_stage_path(stage_id):
    dir_name = None
    stage_row = project.get_stage_data(stage_id)
    if stage_row:
        stage_name = stage_row['name']
        asset_path = get_asset_path(stage_row['asset_id'])
        if stage_name and asset_path:
            dir_name = os.path.join(asset_path, stage_name)
    return dir_name

def get_variant_path(variant_id):
    dir_name = None
    variant_row = project.get_variant_data(variant_id)
    if variant_row:
        variant_name = variant_row['name']
        stage_path = get_stage_path(variant_row['stage_id'])
        if variant_name and stage_path:
            dir_name = os.path.join(stage_path, variant_name)
    return dir_name

def get_variant_export_path(variant_id):
    dir_name = None
    variant_row = project.get_variant_data(variant_id)
    if variant_row:
        variant_name = variant_row['name']
        stage_path = get_stage_path(variant_row['stage_id'])
        if variant_name and stage_path:
            dir_name = os.path.join(stage_path, variant_name, '_EXPORTS')
    return dir_name

def get_work_env_path(work_env_id):
    dir_name = None
    work_env_row = project.get_work_env_data(work_env_id)
    if work_env_row:
        work_env_name = work_env_row['name']
        variant_path = get_variant_path(work_env_row['variant_id'])
        if work_env_name and variant_path:
            dir_name = os.path.join(variant_path, work_env_name)
    return dir_name

def get_export_path(export_id):
    dir_name = None
    export_row = project.get_export_data(export_id)
    if export_row:
        export_name = export_row['name']
        variant_path = get_variant_path(export_row['variant_id'])
        if export_name and variant_path:
            dir_name = os.path.join(variant_path, '_EXPORTS', export_name)
    return dir_name

def get_export_version_path(export_version_id):
    dir_name = None
    export_version_row = project.get_export_version_data(export_version_id)
    if export_version_row:
        export_version_name = export_version_row['name']
        export_path = get_export_path(export_version_row['export_id'])
        if export_version_name and export_path:
            dir_name = os.path.join(export_path, export_version_name)
    return dir_name

def build_version_file_name(work_env_id, name):
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    extension = project.get_software_data(work_env_row['software_id'],
                                                'extension')
    file_name = f"{category_row['name']}"
    file_name += f"_{asset_row['name']}"
    file_name += f"_{stage_row['name']}"
    file_name += f"_{variant_row['name']}"
    file_name += f".{name}"
    file_name += f".{extension}"
    return file_name

def build_export_file_name(work_env_id, export_name, multiple=None):
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    '''
    extension = work_env_row['export_extension']
    if not extension:
    '''
    if not work_env_row['export_extension']:
        extension = project.get_default_extension(stage_row['name'], work_env_row['software_id'])
    else:
        extension = work_env_row['export_extension']

    if extension:
        file_name = f"{category_row['name']}"
        file_name += f"_{asset_row['name']}"
        file_name += f"_{stage_row['name']}"
        file_name += f"_{variant_row['name']}"
        file_name += f"_{export_name}"
        if multiple:
            file_name += f".{multiple}"
        file_name += f".{extension}"
        return file_name
    else:
        logger.error("Can't build file name")
        return None

def build_namespace(export_version_id):
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    variant_row = project.get_variant_data(export_row['variant_id'])
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    domain_row = project.get_domain_data(category_row['domain_id'])
    namespace = f"{category_row['name']}" 
    namespace += f"_{asset_row['name']}" 
    namespace += f"_{stage_row['name'][:3]}"
    return namespace

def instance_to_string(instance_tuple):
    instance_type = instance_tuple[0]
    instance_id = instance_tuple[-1]
    string = None
    if instance_type == 'export_version':
        export_version_row = project.get_export_version_data(instance_id)
        export_row = project.get_export_data(export_version_row['export_id'])
        variant_row = project.get_variant_data(export_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
        string+=f"/{stage_row['name']}/{variant_row['name']}/{export_row['name']}/{export_version_row['name']}"
    elif instance_type == 'export':
        export_row = project.get_export_data(instance_id)
        variant_row = project.get_variant_data(export_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
        string+=f"/{stage_row['name']}/{variant_row['name']}/{export_row['name']}"
    elif instance_type == 'work_version':
        version_row = project.get_version_data(instance_id)
        work_env_row = project.get_work_env_data(version_row['work_env_id'])
        variant_row = project.get_variant_data(work_env_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
        string+=f"/{stage_row['name']}/{variant_row['name']}/{work_env_row['name']}/{version_row['name']}"
    elif instance_type == 'work_env':
        work_env_row = project.get_work_env_data(instance_id)
        variant_row = project.get_variant_data(work_env_row['variant_id'])
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
        string+=f"/{stage_row['name']}/{variant_row['name']}/{work_env_row['name']}"
    elif instance_type == 'variant':
        variant_row = project.get_variant_data(instance_id)
        stage_row = project.get_stage_data(variant_row['stage_id'])
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
        string+=f"/{stage_row['name']}/{variant_row['name']}"
    elif instance_type == 'stage':
        stage_row = project.get_stage_data(instance_id)
        asset_row = project.get_asset_data(stage_row['asset_id'])
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
        string+=f"/{stage_row['name']}"
    elif instance_type == 'asset':
        asset_row = project.get_asset_data(instance_id)
        category_row = project.get_category_data(asset_row['category_id'])
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}/{asset_row['name']}"
    elif instance_type == 'category':
        category_row = project.get_category_data(instance_id)
        domain_row = project.get_domain_data(category_row['domain_id'])
        string=f"{domain_row['name']}/{category_row['name']}"
    elif instance_type == 'domain':
        domain_row = project.get_domain_data(instance_id)
        string=f"{domain_row['name']}"
    return string

def string_to_instance(string):
    instances_list = string.split('/')

    if len(instances_list) == 1:
        instance_type = 'domain'
        instance_id = project.get_domain_by_name(instances_list[0], 'id')
    elif len(instances_list) ==2:
        instance_type = 'category'
        domain_id = project.get_domain_by_name(instances_list[0], 'id')
        instance_id = project.get_domain_child_by_name(domain_id, instances_list[1], 'id')
    elif len(instances_list) == 3:
        instance_type = 'asset'
        domain_id = project.get_domain_by_name(instances_list[0], 'id')
        category_id = project.get_domain_child_by_name(domain_id, instances_list[1], 'id')
        instance_id = project.get_category_child_by_name(category_id, instances_list[2], 'id')
    elif len(instances_list) == 4:
        instance_type = 'stage'
        domain_id = project.get_domain_by_name(instances_list[0], 'id')
        category_id = project.get_domain_child_by_name(domain_id, instances_list[1], 'id')
        asset_id = project.get_category_child_by_name(category_id, instances_list[2], 'id')
        instance_id = project.get_asset_child_by_name(asset_id, instances_list[3], 'id')
    elif len(instances_list) == 5:
        instance_type = 'variant'
        domain_id = project.get_domain_by_name(instances_list[0], 'id')
        category_id = project.get_domain_child_by_name(domain_id, instances_list[1], 'id')
        asset_id = project.get_category_child_by_name(category_id, instances_list[2], 'id')
        stage_id = project.get_asset_child_by_name(asset_id, instances_list[3], 'id')
        instance_id = project.get_stage_child_by_name(stage_id, instances_list[4], 'id')

    return (instance_type, instance_id)

def string_to_work_instance(string):
    instances_list = string.split('/')
    if len(instances_list) == 6:
        instance_type = 'work_env'
        work_env_name = instances_list.pop(-1)
        _, variant_id = string_to_instance(('/').join(instances_list))
        instance_id = project.get_variant_work_env_child_by_name(variant_id, work_env_name, 'id')
    elif len(instances_list) == 7:
        instance_type = 'work_version'
        work_version_name = instances_list.pop(-1)
        work_env_name = instances_list.pop(-1)
        _, variant_id = string_to_instance(('/').join(instances_list))
        work_env_id = project.get_variant_work_env_child_by_name(variant_id, work_env_name, 'id')
        instance_id = project.get_work_version_by_name(work_env_id, work_version_name, 'id')

    return (instance_type, instance_id)
