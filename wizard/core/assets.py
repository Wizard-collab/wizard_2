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
import clipboard
import traceback

# Wizard modules
from wizard.core import environment
from wizard.core import events
from wizard.core import project
from wizard.core import repository
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import image
from wizard.core import game
from wizard.core import tags
from wizard.core import stats
from wizard.core import asset_tracking
from wizard.core import hooks
from wizard.core import user
from wizard.vars import assets_vars
from wizard.vars import env_vars
from wizard.vars import softwares_vars
from wizard.vars import game_vars

logger = logging.getLogger(__name__)

def create_domain(name):
    domain_id = None
    if tools.is_safe(name):
        dir_name = path_utils.clean_path(path_utils.join(environment.get_project_path(),
                                    name))
        domain_id = project.add_domain(name)
        if domain_id:
            if not tools.create_folder(dir_name):
                project.remove_domain(domain_id)
                domain_id = None
    return domain_id

def archive_domain(domain_id):
    if repository.is_admin():
        domain_row = project.get_domain_data(domain_id)
        if domain_row:
            dir_name = get_domain_path(domain_id)
            if path_utils.isdir(dir_name):
                if tools.make_archive(dir_name):
                    path_utils.rmtree(dir_name)
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
            dir_name = path_utils.clean_path(path_utils.join(domain_path, name))
            category_id = project.add_category(name, domain_id)
            if category_id:
                if not tools.create_folder(dir_name):
                    project.remove_category(category_id)
                    category_id = None
                else:
                    events.add_creation_event('category', category_id)
                    game.add_xps(game_vars._creation_xp_)
        else:
            logger.error("Can't create category")
    return category_id

def archive_category(category_id):
    if repository.is_admin():
        category_row = project.get_category_data(category_id)
        if category_row:
            dir_name = get_category_path(category_id)
            if path_utils.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    path_utils.rmtree(dir_name)
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
            dir_name = path_utils.clean_path(path_utils.join(category_path, name))
            asset_id = project.add_asset(name, category_id, inframe, outframe, preroll, postroll)
            if asset_id:
                if not tools.create_folder(dir_name):
                    project.remove_asset(asset_id)
                    asset_id = None
                else:
                    events.add_creation_event('asset', asset_id)
                    game.add_xps(game_vars._creation_xp_)
        else:
            logger.error("Can't create asset")
    return asset_id

def modify_asset_frame_range(asset_id, inframe, outframe, preroll, postroll):
    success = project.modify_asset_frame_range(asset_id, inframe, outframe, preroll, postroll)
    if success:
        logger.info("Frame range modified")
    return success

def archive_asset(asset_id):
    if repository.is_admin():
        asset_row = project.get_asset_data(asset_id)
        if asset_row:
            dir_name = get_asset_path(asset_id)
            if path_utils.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    path_utils.rmtree(dir_name)
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

def get_asset_data_from_work_env_id(work_env_id, column='*'):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    asset_id = project.get_stage_data(stage_id, 'asset_id')
    if asset_id:
        asset_row = project.get_asset_data(asset_id, column)
        return asset_row
    else:
        return None

def get_stage_data_from_work_env_id(work_env_id, column='*'):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if stage_id:
        stage_row = project.get_stage_data(stage_id, column)
        return stage_row
    else:
        return None

def get_domain_data_from_work_env_id(work_env_id, column='*'):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    domain_id = project.get_stage_data(stage_id, 'domain_id')
    if domain_id:
        domain_row = project.get_domain_data(domain_id, column)
        return domain_row
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
            dir_name = path_utils.clean_path(path_utils.join(asset_path, name))
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
    if repository.is_admin():
        stage_row = project.get_stage_data(stage_id)
        if stage_row:
            dir_name = get_stage_path(stage_id)
            if path_utils.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    path_utils.rmtree(dir_name)
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
            dir_name = path_utils.clean_path(path_utils.join(stage_path, name))
            
            variant_id = project.add_variant(name, stage_id, comment)
            if variant_id:
                if not tools.create_folder(dir_name):
                    project.remove_variant(variant_id)
                    variant_id = None
                else:
                    # Add other folders
                    tools.create_folder(path_utils.clean_path(path_utils.join(dir_name, '_EXPORTS')))
                    tools.create_folder(path_utils.clean_path(path_utils.join(dir_name, '_SANDBOX')))
                    tools.create_folder(path_utils.clean_path(path_utils.join(dir_name, '_VIDEOS')))
                    events.add_creation_event('variant', variant_id)
                    game.add_xps(game_vars._creation_xp_)
        else:
            logger.error("Can't create variant")
    return variant_id

def archive_variant(variant_id):
    if repository.is_admin():
        variant_row = project.get_variant_data(variant_id)
        if variant_row:
            dir_name = get_variant_path(variant_id)
            if path_utils.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    path_utils.rmtree(dir_name)
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

def modify_stage_state(stage_id, state, comment=''):
    if state in assets_vars._asset_states_list_:
        project.set_stage_data(stage_id, 'state', state)
        if comment is not None and comment != '':
            project.set_stage_data(stage_id, 'tracking_comment', comment)
        project.update_stage_progress(stage_id)
        asset_tracking.add_state_switch_event(stage_id, state, comment)
    else:
        logger.warning(f"Unknown state {state}")

def add_stage_comment(stage_id, comment):
    project.set_stage_data(stage_id, 'tracking_comment', comment)
    asset_tracking.add_comment_event(stage_id, comment)

def modify_stage_assignment(stage_id, user_name):
    user_id = repository.get_user_row_by_name(user_name, 'id')
    if user_id in project.get_users_ids_list():
        project.set_stage_data(stage_id, 'assignment', user_name)
        asset_tracking.add_assignment_event(stage_id, user_name)
    else:
        logger.warning(f"{user_name} never logged into project")

def modify_stage_estimation(stage_id, seconds):
    if type(seconds) == int:
        project.set_stage_data(stage_id, 'estimated_time', seconds)
        project.update_stage_progress(stage_id)
        asset_tracking.add_estimation_event(stage_id, seconds)
    else:
        logger.warning(f'{seconds} is not a int')

def add_work_time(work_env_id, work_time):
    project.add_work_time(work_env_id, work_time)
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    project.add_stage_work_time(stage_id, work_time)
    project.update_stage_progress(stage_id)
    asset_tracking.add_work_session_event(stage_id, work_time)

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
            dir_name = path_utils.clean_path(path_utils.join(variant_path, name))
            screenshots_dir_name = path_utils.clean_path(path_utils.join(dir_name, 'screenshots'))
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

def force_unlock(work_env_id):
    project.set_work_env_lock(work_env_id, 0)

def create_references_from_variant_id(work_env_id, variant_id):
    export_rows = project.get_variant_export_childs(variant_id)
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    stage = project.get_stage_data(stage_id, 'name')

    if export_rows is not None:
        if stage in [assets_vars._modeling_, assets_vars._layout_]:
            export_rows = [export_rows[0]]
        at_least_one = False
        for export_row in export_rows:
            export_version_id = project.get_default_export_version(export_row['id'], 'id')
            if export_version_id:
                at_least_one = True
                create_reference(work_env_id, export_version_id)
        if at_least_one:
            return 1
        else:
            logger.warning('No export found')
            return None
    else:
        return None

def create_reference(work_env_id,
                        export_version_id,
                        namespace_and_count=None,
                        auto_update=None):
    if auto_update is None:
        auto_update = user.user().get_reference_auto_update_default()
    if not namespace_and_count:
        namespaces_list = project.get_references(work_env_id, 'namespace')
        count = 0
        namespace_raw = build_namespace(export_version_id)
        namespace = f"{namespace_raw}"
        while namespace in namespaces_list:
            count+=1
            namespace = f"{namespace_raw}_{str(count)}"
    else:
        namespace = namespace_and_count[0]
        count = namespace_and_count[1]
    return project.create_reference(work_env_id,
                                            export_version_id,
                                            namespace,
                                            count,
                                            int(auto_update))

def remove_reference(reference_id):
    return project.remove_reference(reference_id)

def set_reference_last_version(reference_id):
    export_version_id = project.get_reference_data(reference_id, 'export_version_id')
    if export_version_id is not None:
        export_version_row = project.get_export_version_data(export_version_id)
        export_row = project.get_export_data(export_version_row['export_id'])
        default_export_version_id = project.get_default_export_version(export_row['id'], 'id')
        if default_export_version_id:
            if default_export_version_id != export_version_id:
                project.update_reference(reference_id, default_export_version_id)
                return 1
            else:
                logger.info("Reference is up to date")
                return None

def modify_reference_LOD(work_env_id, LOD, namespaces_list):
    references_rows = project.get_references(work_env_id)
    for reference_row in references_rows:
        if reference_row['namespace'] in namespaces_list:
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
        if reference_files_list == []:
            reference_files_list = get_export_files_list(reference_row['export_version_id'])
        variant_id = project.get_export_data(reference_row['export_id'], 'variant_id')
        variant_row = project.get_variant_data(variant_id)
        variant_name = variant_row['name']
        string_variant = variant_row['string']
        asset_id = project.get_stage_data(variant_row['stage_id'], 'asset_id')
        asset_row = project.get_asset_data(asset_id)
        asset_name = asset_row['name']
        category_name = project.get_category_data(asset_row['category_id'], 'name')
        reference_dic = dict()
        reference_dic['files'] = reference_files_list
        reference_dic['namespace'] = reference_row['namespace']
        reference_dic['count'] = reference_row['count']
        reference_dic['category_name'] = category_name
        reference_dic['asset_name'] = asset_name
        reference_dic['variant_name'] = variant_name
        reference_dic['string_variant'] = string_variant
        if reference_row['stage'] not in references_dic.keys():
            references_dic[reference_row['stage']] = []
        references_dic[reference_row['stage']].append(reference_dic)
    referenced_groups_rows = project.get_referenced_groups(work_env_id)
    for referenced_group_row in referenced_groups_rows:
        grouped_references_rows = project.get_grouped_references(referenced_group_row['group_id'])
        for grouped_reference_row in grouped_references_rows:
            reference_files_list = json.loads(project.get_export_version_data(grouped_reference_row['export_version_id'], 'files'))
            if reference_files_list == []:
                reference_files_list = get_export_files_list(reference_row['export_version_id'])
            variant_id = project.get_export_data(grouped_reference_row['export_id'], 'variant_id')
            variant_row = project.get_variant_data(variant_id)
            variant_name = variant_row['name']
            string_variant = variant_row['string']
            asset_id = project.get_stage_data(variant_row['stage_id'], 'asset_id')
            asset_row = project.get_asset_data(asset_id)
            asset_name = asset_row['name']
            category_name = project.get_category_data(asset_row['category_id'], 'name')
            reference_dic = dict()
            reference_dic['files'] = reference_files_list
            reference_dic['namespace'] = f"{referenced_group_row['namespace']}_{grouped_reference_row['namespace']}"
            reference_dic['count'] = f"{referenced_group_row['count']}_{grouped_reference_row['count']}"
            reference_dic['category_name'] = category_name
            reference_dic['asset_name'] = asset_name
            reference_dic['variant_name'] = variant_name
            reference_dic['string_variant'] = string_variant
            if grouped_reference_row['stage'] not in references_dic.keys():
                references_dic[grouped_reference_row['stage']] = []
            references_dic[grouped_reference_row['stage']].append(reference_dic)
    return references_dic

def get_export_files_list(export_version_id):
    export_version_path = get_export_version_path(export_version_id)
    files_list = []
    for file in path_utils.listdir(export_version_path):
        files_list.append(path_utils.join(export_version_path, file))
    return files_list

def merge_file_as_export_version(export_name, files, variant_id, comment='', execute_xp=True):
    return add_export_version(export_name, files, variant_id, None, comment, skip_temp_purge=True)

def add_export_version_from_version_id(export_name, files, version_id, comment='', execute_xp=True):
    work_env_row = project.get_work_env_data(project.get_version_data(version_id, 'work_env_id'))
    if work_env_row is not None:
        variant_id = work_env_row['variant_id']
        return add_export_version(export_name, files, variant_id, version_id, comment, execute_xp)

def add_export_version(export_name, files, variant_id, version_id, comment='', execute_xp=True, skip_temp_purge=False):
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
    if extension_errors != []:
        for file in extension_errors:
            logger.warning(f"{file} format doesn't math the stage export rules ( {(', ').join(extensions_rules)} )")
        return
    if not variant_row:
        return
    export_id = get_or_add_export(export_name, variant_id)
    if not export_id:
        return
    last_version_name = project.get_last_export_version(export_id, 'name')
    if last_version_name:
        new_version =  str(int(last_version_name)+1).zfill(4)
    else:
        new_version = '0001'

    export_path = get_export_path(export_id)
    if not export_path:
        return
    dir_name = path_utils.clean_path(path_utils.join(export_path, new_version))
    while path_utils.isdir(dir_name):
        new_version = str(int(new_version)+1).zfill(4)
        dir_name = path_utils.clean_path(path_utils.join(export_path, new_version))
    if not tools.create_folder(dir_name):
        return
    copied_files = tools.copy_files(files, dir_name)
    if copied_files is None:
        if not tools.remove_folder(dir_name):
            logger.warning(f"{dir_name} can't be removed, keep export version {new_version} in database")
        return
    export_version_id = project.add_export_version(new_version,
                                                    copied_files,
                                                    export_id,
                                                    version_id,
                                                    comment)
    if (len(copied_files) == len(files) and len(files) > 0) and not skip_temp_purge:
        tools.remove_tree(os.path.dirname(files[0]))
    elif len(copied_files) != len(files):
        logger.warning(f"Missing files, keeping temp dir: {os.path.dirname(files[0])}")
    else:
        pass
    game.add_xps(game_vars._export_xp_)
    if execute_xp:
        game.analyse_comment(comment, game_vars._export_penalty_)
    events.add_export_event(export_version_id)
    tags.analyse_comment(comment, 'export_version', export_version_id)
    # Trigger after export hook
    export_version_string = instance_to_string(('export_version', export_version_id))
    hooks.after_export_hooks(export_version_string=export_version_string,
                                export_dir=dir_name,
                                stage_name=stage_name)
    return export_version_id
        

def modify_export_version_comment(export_version_id, comment):
    success = project.modify_export_version_comment(export_version_id, comment)
    if success:
        tags.analyse_comment(comment, 'export_version', export_version_id)
    return success

def modify_video_comment(video_id, comment):
    success = project.modify_video_comment(video_id, comment)
    if success:
        tags.analyse_comment(comment, 'video', video_id)
    return success


def request_export(work_env_id, export_name, multiple=None, only_dir=None):
    # Gives a temporary ( and local ) export file name
    # for the softwares
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if variant_id:
        export_id = get_or_add_export(export_name, variant_id)
        if export_id:
            export_path = get_temp_export_path(export_id)
            path_utils.makedirs(export_path)
            dir_name = tools.temp_dir_in_dir(export_path)
            logger.info(f"Temporary directory created : {dir_name}, if something goes wrong in the export please go there to find your temporary export file")
            file_name = build_export_file_name(work_env_id, export_name, multiple)
            if file_name and not only_dir:
                return path_utils.clean_path(path_utils.join(dir_name, file_name))
            elif file_name and only_dir:
                return dir_name

def request_render(version_id, export_name, comment=''):
    work_env_id = project.get_version_data(version_id, 'work_env_id')
    if work_env_id:
        variant_id = project.get_work_env_data(work_env_id, 'variant_id')
        if variant_id:
            export_version_id = add_export_version(export_name, [], variant_id, version_id, comment)
            if export_version_id:
                export_version_path = get_export_version_path(export_version_id)
                return export_version_path

def archive_export(export_id):
    if repository.is_admin():
        export_row = project.get_export_data(export_id)
        if export_row:
            dir_name = get_export_path(export_id)
            if path_utils.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    path_utils.rmtree(dir_name)
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
            dir_name = path_utils.clean_path(path_utils.join(variant_path, '_EXPORTS', name))
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
    return export_id

def archive_export_version(export_version_id):
    if repository.is_admin():
        export_version_row = project.get_export_version_data(export_version_id)
        export_id = export_version_row['export_id']
        if export_version_row:
            dir_name = get_export_version_path(export_version_id)
            if path_utils.isdir(dir_name):
                archive_file = tools.make_archive(dir_name)
                if archive_file:
                    path_utils.rmtree(dir_name)
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

def screen_over_version(version_id):
    version_row = project.get_version_data(version_id)
    if not version_row:
        return
    screenshot_file, thumbnail_file = image.screenshot(version_row['screenshot_path'], version_row['thumbnail_path'])
    return project.modify_version_screen(version_id, screenshot_file, thumbnail_file)

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
    screenshot_dir_name = path_utils.join(dirname, 'screenshots')

    file_name = path_utils.clean_path(path_utils.join(dirname, 
                            build_version_file_name(work_env_id, new_version)))
    file_name_ext = os.path.splitext(file_name)[-1]

    basename = os.path.basename(file_name)
    screenshot_file = path_utils.join(screenshot_dir_name, 
                    basename.replace(file_name_ext, '.jpg'))
    thumbnail_file = path_utils.join(screenshot_dir_name, 
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
    if version_id:
        game.add_xps(game_vars._save_xp_)
    if (analyse_comment and not fresh) and version_id:
        game.analyse_comment(comment, game_vars._save_penalty_)

    tags.analyse_comment(comment, 'work_version', version_id)

    return version_id

def add_video(variant_id, comment="", analyse_comment=None):
    last_version_list = project.get_last_video_version(variant_id, 'name')
    if len(last_version_list) == 1:
        last_version = last_version_list[0]
        new_version =  str(int(last_version)+1).zfill(4)
    else:
        new_version = '0001'

    dirname = get_video_path(variant_id)
    if not path_utils.isdir(dirname):
        path_utils.mkdir(dirname)
    screenshot_dir_name = path_utils.join(dirname, 'thumbnails')
    if not path_utils.isdir(screenshot_dir_name):
        path_utils.mkdir(screenshot_dir_name)

    file_name = path_utils.clean_path(path_utils.join(dirname, 
                            build_video_file_name(variant_id, new_version)))
    file_name_ext = os.path.splitext(file_name)[-1]

    basename = os.path.basename(file_name)
    thumbnail_file = path_utils.join(screenshot_dir_name, 
                    basename.replace(file_name_ext, '.thumbnail.jpg'))


    video_id = project.add_video(new_version,
                                file_name,
                                variant_id,
                                comment,
                                thumbnail_file)
    if video_id:
        events.add_video_event(video_id, variant_id)
        game.add_xps(game_vars._video_xp_)
        tags.analyse_comment(comment, 'video', video_id)
    if analyse_comment and video_id:
        game.analyse_comment(comment, game_vars._video_penalty_)

    return video_id

def copy_work_version(work_version_id):
    clipboard_dic = dict()
    clipboard_dic['work_version_id'] = work_version_id
    clipboard.copy(json.dumps(clipboard_dic))
    logger.info("Version ID copied to clipboard")

def paste_work_version(destination_work_env_id, mirror_work_env_references=False):
    clipboard_json = clipboard.paste()
    try:
        clipboard_dic = json.loads(clipboard_json)
    except json.decoder.JSONDecodeError:
        logger.warning("No valid work version found in clipboard")
        return
    if 'work_version_id' not in clipboard_dic.keys():
        logger.warning("No valid work version found in clipboard")
        return
    work_version_id = clipboard_dic['work_version_id']
    if not duplicate_version(work_version_id, work_env_id=destination_work_env_id):
        return
    if mirror_work_env_references:
        work_version_row = project.get_version_data(work_version_id)
        work_env_id = work_version_row['work_env_id']
        mirror_references(work_env_id, destination_work_env_id)

def mirror_references(work_env_id, destination_work_env_id):
    for reference_id in project.get_references(destination_work_env_id, 'id'):
        remove_reference(reference_id)
    for reference_row in project.get_references(work_env_id):
        create_reference(destination_work_env_id,
                                reference_row['export_version_id'],
                                namespace_and_count=[reference_row['namespace'], reference_row['count']],
                                auto_update=reference_row['auto_update'])

def modify_version_comment(version_id, comment=''):
    success = project.modify_version_comment(version_id, comment)
    if success:
        tags.analyse_comment(comment, 'work_version', version_id)
    return success

def set_asset_preview(asset_id, image_file):
    if image_file is not None:
        preview_path = path_utils.join(get_asset_path(asset_id), 'preview')
        if not path_utils.isdir(preview_path):
            path_utils.mkdir(preview_path)
        destination = path_utils.join(preview_path, f"{project.get_asset_data(asset_id, 'name')}.jpg")
        preview_file = image.resize_preview(image_file, destination)
    else:
        preview_file = None
    project.modify_asset_manual_preview(asset_id, preview_file)

def merge_file(file, work_env_id, comment="", do_screenshot=1):
    if path_utils.isfile(file):
        software_extension = project.get_software_data(project.get_work_env_data(work_env_id, 'software_id'), 'extension')
        file_extension = os.path.splitext(file)[-1].replace('.', '')
        if software_extension == file_extension:
            version_id = add_version(work_env_id, comment, do_screenshot)
            version_row = project.get_version_data(version_id)
            path_utils.copyfile(file, version_row['file_path'])
            logger.info(f"{file} merged in new version {version_row['name']}")
            return version_id
        else:
            logger.warning(f"{file} doesn't match the work environment extension rules ( .ma )")
            return None
    else:
        logger.warning(f"{file} doesn't exists")
        return None

def duplicate_version(version_id, work_env_id=None, comment=None):
    new_version_id = None
    version_row = project.get_version_data(version_id)
    if version_row is not None:
        if comment is None:
            comment = version_row['comment']
        if work_env_id is None:
            work_env_id = version_row['work_env_id']
        new_version_id = merge_file(version_row['file_path'],
                                    work_env_id,
                                    comment, 0)
        if new_version_id is None:
            return
        new_version_row = project.get_version_data(new_version_id)
        if path_utils.isfile(version_row['screenshot_path']):
            path_utils.copyfile(version_row['screenshot_path'], new_version_row['screenshot_path'])
        if path_utils.isfile(version_row['thumbnail_path']):
            path_utils.copyfile(version_row['thumbnail_path'], new_version_row['thumbnail_path'])
    return new_version_id

def archive_version(version_id):
    if repository.is_admin():
        version_row = project.get_version_data(version_id)
        if version_row['name'] != '0001':
            if version_row:
                if path_utils.isfile(version_row['file_path']):
                    zip_file = path_utils.join(os.path.split(version_row['file_path'])[0], 
                                'archives.zip')
                    if tools.zip_files([version_row['file_path']], zip_file):
                        path_utils.remove(version_row['file_path'])
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

def archive_video(video_id):
    if repository.is_admin():
        video_row = project.get_video_data(video_id)
        if video_row:
            if path_utils.isfile(video_row['file_path']):
                zip_file = path_utils.join(os.path.split(video_row['file_path'])[0], 
                            'archives.zip')
                if tools.zip_files([video_row['file_path']], zip_file):
                    path_utils.remove(video_row['file_path'])
                    path_utils.remove(video_row['thumbnail_path'])
                    logger.info(f"{video_row['file_path']} deleted")
            else:
                logger.warning(f"{video_row['file_path']} not found")
            success = project.remove_video(video_row['id'])
            return success
        else:
            return None    
    else:
        return None

def get_video_folder(version_id):
    version_row = project.get_version_data(version_id)
    work_env_path = get_work_env_path(version_row['work_env_id'])
    playblast_folder = path_utils.join(work_env_path, 'video')
    if not path_utils.isdir(playblast_folder):
        path_utils.mkdir(playblast_folder)
    return playblast_folder

def create_group(name, color='#798fe8'):
    if tools.is_safe(name):
        return project.create_group(name, color)

def remove_group(group_id):
    return project.remove_group(group_id)

def create_referenced_group(work_env_id, group_id):
    namespaces_list = project.get_referenced_groups(work_env_id, 'namespace')
    count = 0
    namespace_raw = project.get_group_data(group_id, 'name')
    namespace = f"{namespace_raw}"
    while namespace in namespaces_list:
        count+=1
        namespace = f"{namespace_raw}_{str(count)}"
    return project.create_referenced_group(work_env_id,
                                            group_id,
                                            namespace,
                                            count)

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
            export_version_id = project.get_default_export_version(export_row['id'], 'id')
            if export_version_id:
                create_grouped_reference(group_id, export_version_id)
        return 1
    else:
        return None

def create_grouped_reference(group_id, export_version_id):
    namespaces_list = project.get_grouped_references(group_id, 'namespace')
    count = 0
    namespace_raw = build_namespace(export_version_id)
    namespace = f"{namespace_raw}"
    while namespace in namespaces_list:
        count+=1
        namespace = f"{namespace_raw}_{str(count)}"
    return project.create_grouped_reference(group_id,
                                            export_version_id,
                                            namespace,
                                            count)

def remove_grouped_reference(grouped_reference_id):
    return project.remove_grouped_reference(grouped_reference_id)

def set_grouped_reference_last_version(grouped_reference_id):
    export_version_id = project.get_grouped_reference_data(grouped_reference_id, 'export_version_id')
    if export_version_id is not None:
        export_version_row = project.get_export_version_data(export_version_id)
        export_row = project.get_export_data(export_version_row['export_id'])
        default_export_version_id = project.get_default_export_version(export_row['id'], 'id')
        if default_export_version_id:
            if default_export_version_id != export_version_id:
                project.update_grouped_reference(grouped_reference_id, default_export_version_id)
                return 1
            else:
                logger.info("Grouped reference is up to date")
                return None

def create_or_get_camera_work_env(work_env_id):
    work_env_row = project.get_work_env_data(work_env_id)
    software = work_env_row['name']
    stage_id = project.get_variant_data(work_env_row['variant_id'], 'stage_id')
    asset_id = project.get_stage_data(stage_id, 'asset_id')
    stages = project.get_asset_childs(asset_id, 'name')
    if 'camera' in stages:
        camera_stage_id = project.get_asset_child_by_name(asset_id, 'camera', 'id')
    else:
        camera_stage_id = create_stage('camera', asset_id)
    camera_default_variant_id = project.get_stage_data(camera_stage_id, 'default_variant_id')
    work_envs = project.get_variant_work_envs_childs(camera_default_variant_id, 'name')
    if software in work_envs:
        camera_work_env_id = project.get_variant_work_env_child_by_name(camera_default_variant_id, software, 'id')
    else:
        software_id = project.get_software_data_by_name(software, 'id')
        camera_work_env_id = create_work_env(software_id, camera_default_variant_id)
    return camera_work_env_id

def add_asset_tracking_event(stage_id, event_type, data, comment=''):
    success = project.add_asset_tracking_event(stage_id, event_type, data, comment)
    if success:
        tags.analyse_comment(comment, 'stage', stage_id)
    return success

def get_default_extension(work_env_id):
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_name = project.get_stage_data(variant_row['stage_id'], 'name')
    if not work_env_row['export_extension']:
        extension = project.get_default_extension(stage_name, work_env_row['software_id'])
    else:
        extension = work_env_row['export_extension']
    return extension

def get_domain_path(domain_id):
    dir_name = None
    domain_name = project.get_domain_data(domain_id, 'name')
    if domain_name:
        dir_name = path_utils.join(environment.get_project_path(), domain_name)
    return dir_name

def get_category_path(category_id):
    dir_name = None
    category_row = project.get_category_data(category_id)
    if category_row:
        category_name = category_row['name']
        domain_path = get_domain_path(category_row['domain_id'])
        if category_name and domain_path:
            dir_name = path_utils.join(domain_path, category_name)
    return dir_name

def get_asset_path(asset_id):
    dir_name = None
    asset_row = project.get_asset_data(asset_id)
    if asset_row:
        asset_name = asset_row['name']
        category_path = get_category_path(asset_row['category_id'])
        if asset_name and category_path:
            dir_name = path_utils.join(category_path, asset_name)
    return dir_name

def get_stage_path(stage_id):
    dir_name = None
    stage_row = project.get_stage_data(stage_id)
    if stage_row:
        stage_name = stage_row['name']
        asset_path = get_asset_path(stage_row['asset_id'])
        if stage_name and asset_path:
            dir_name = path_utils.join(asset_path, stage_name)
    return dir_name

def get_variant_path(variant_id):
    dir_name = None
    variant_row = project.get_variant_data(variant_id)
    if variant_row:
        variant_name = variant_row['name']
        stage_path = get_stage_path(variant_row['stage_id'])
        if variant_name and stage_path:
            dir_name = path_utils.join(stage_path, variant_name)
    return dir_name

def get_variant_export_path(variant_id):
    dir_name = None
    variant_row = project.get_variant_data(variant_id)
    if variant_row:
        variant_name = variant_row['name']
        stage_path = get_stage_path(variant_row['stage_id'])
        if variant_name and stage_path:
            dir_name = path_utils.join(stage_path, variant_name, '_EXPORTS')
    return dir_name

def get_work_env_path(work_env_id):
    dir_name = None
    work_env_row = project.get_work_env_data(work_env_id)
    if work_env_row:
        work_env_name = work_env_row['name']
        variant_path = get_variant_path(work_env_row['variant_id'])
        if work_env_name and variant_path:
            dir_name = path_utils.join(variant_path, work_env_name)
    return dir_name

def get_video_path(variant_id):
    dir_name = None
    variant_path = get_variant_path(variant_id)
    if variant_path:
        dir_name = path_utils.join(variant_path, '_VIDEOS')
        if not path_utils.isdir(dir_name):
            path_utils.mkdir(dir_name)
    return dir_name

def get_export_path(export_id):
    dir_name = None
    export_row = project.get_export_data(export_id)
    if export_row:
        export_name = export_row['name']
        variant_path = get_variant_path(export_row['variant_id'])
        if export_name and variant_path:
            dir_name = path_utils.join(variant_path, '_EXPORTS', export_name)
    return dir_name

def get_temp_export_path(export_id):
    dir_name = None

    local_path = user.user().get_local_path()
    project_path = environment.get_project_path()

    if local_path is None or local_path == '':
        dir_name = tools.temp_dir()
        logger.warning("Your local path is not setted, exporting in default temp dir.")
        return dir_name

    export_row = project.get_export_data(export_id)
    if export_row:
        export_name = export_row['name']
        variant_path = get_variant_path(export_row['variant_id'])
        if export_name and variant_path:
            dir_name = path_utils.join(variant_path, '_EXPORTS', export_name, 'temp')
            dir_name = local_path+dir_name[len(project_path):]
            return dir_name

def get_temp_video_path(variant_id):
    dir_name = None

    local_path = user.user().get_local_path()
    project_path = environment.get_project_path()

    if local_path is None or local_path == '':
        dir_name = tools.temp_dir()
        logger.warning("Your local path is not setted, exporting in default temp dir.")
        return dir_name

    video_path = get_video_path(variant_id)
    dir_name = path_utils.join(video_path, 'temp')
    dir_name = local_path+dir_name[len(project_path):]
    if not path_utils.isdir(dir_name):
        path_utils.makedirs(dir_name)
    dir_name = tools.temp_dir_in_dir(dir_name)
    return dir_name

def get_export_version_path(export_version_id):
    dir_name = None
    export_version_row = project.get_export_version_data(export_version_id)
    if export_version_row:
        export_version_name = export_version_row['name']
        export_path = get_export_path(export_version_row['export_id'])
        if export_version_name and export_path:
            dir_name = path_utils.join(export_path, export_version_name)
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

def build_video_file_name(variant_id, name):
    variant_row = project.get_variant_data(variant_id)
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    extension = 'mp4' 

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
    if stage_row['name'] == 'animation' or stage_row['name'] == 'cfx':
        namespace += f"_{export_row['name']}"
    namespace += f"_{stage_row['name'][:3]}"
    return namespace

def instance_to_string(instance_tuple):
    instance_type = instance_tuple[0]
    instance_id = instance_tuple[-1]
    string = None
    if instance_type == 'export_version':
        string = project.get_export_version_data(instance_id, 'string')
    elif instance_type == 'export':
        string = project.get_export_data(instance_id, 'string')
    elif instance_type == 'work_version':
        string = project.get_version_data(instance_id, 'string')
    elif instance_type == 'work_env':
        string = project.get_work_env_data(instance_id, 'string')
    elif instance_type == 'variant':
        string = project.get_variant_data(instance_id, 'string')
    elif instance_type == 'stage':
        string = project.get_stage_data(instance_id, 'string')
    elif instance_type == 'asset':
        string = project.get_asset_data(instance_id, 'string')
    elif instance_type == 'category':
        string = project.get_category_data(instance_id, 'string')
    elif instance_type == 'domain':
        string = project.get_domain_data(instance_id, 'string')
    return string

def string_to_instance(string):
    instances_list = string.split('/')

    if len(instances_list) == 1:
        instance_type = 'domain'
        instance_id = project.get_domain_data_by_string(string, 'id')
    elif len(instances_list) ==2:
        instance_type = 'category'
        instance_id = project.get_category_data_by_string(string, 'id')
    elif len(instances_list) == 3:
        instance_type = 'asset'
        instance_id = project.get_asset_data_by_string(string, 'id')
    elif len(instances_list) == 4:
        instance_type = 'stage'
        instance_id = project.get_stage_data_by_string(string, 'id')
    elif len(instances_list) == 5:
        instance_type = 'variant'
        instance_id = project.get_variant_data_by_string(string, 'id')

    return (instance_type, instance_id)

def string_to_work_instance(string):
    instance_type = None
    instance_id = None
    instances_list = string.split('/')
    if len(instances_list) == 6:
        instance_type = 'work_env'
        instance_id = project.get_work_env_data_by_string(string, 'id')
    elif len(instances_list) == 7:
        instance_type = 'work_version'
        instance_id = project.get_work_version_data_by_string(string, 'id')
    else:
        logger.warning('The given string is not a work instance')

    return (instance_type, instance_id)

def string_to_export_instance(string):
    instance_type = None
    instance_id = None
    instances_list = string.split('/')
    if len(instances_list) == 6:
        instance_type = 'export'
        instance_id = project.get_export_data_by_string(string, 'id')
    elif len(instances_list) == 7:
        instance_type = 'export_version'
        instance_id = project.get_export_version_data_by_string(string, 'id')
    else:
        logger.warning('The given string is not an export instance')

    return (instance_type, instance_id)