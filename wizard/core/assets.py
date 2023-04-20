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
from wizard.core import subtasks_library
from wizard.core import threaded_copy
from wizard.vars import assets_vars
from wizard.vars import env_vars
from wizard.vars import softwares_vars
from wizard.vars import game_vars

logger = logging.getLogger(__name__)

def create_domain(name):
    if not tools.is_safe(name):
        return
    dir_name = path_utils.clean_path(path_utils.join(environment.get_project_path(),
                                        name))
    domain_id = project.add_domain(name)
    if not domain_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_domain(domain_id)
        return
    return domain_id

def archive_domain(domain_id):
    if not repository.is_admin():
        return
    domain_row = project.get_domain_data(domain_id)
    if not domain_row:
        return
    dir_name = get_domain_path(domain_id)
    if not path_utils.isdir(dir_name):
        logger.warning(f"{dir_name} not found")
        return
    if not tools.make_archive(dir_name):
        return
    path_utils.rmtree(dir_name)
    logger.info(f"{dir_name} deleted")
    return project.remove_domain(domain_id)

def create_category(name, domain_id):
    if not tools.is_safe(name):
        return
    domain_path = get_domain_path(domain_id)
    if not domain_path:
        logger.error("Can't create category")
        return
    category_id = project.add_category(name, domain_id)
    if not category_id:
        return
    dir_name = path_utils.clean_path(path_utils.join(domain_path, name))
    if not tools.create_folder(dir_name):
        project.remove_category(category_id)
        return
    category_row = project.get_category_data(category_id)
    hooks.after_category_creation_hook(category_row['string'], name)
    events.add_creation_event('category', category_id)
    game.add_xps(game_vars._creation_xp_)
    return category_id

def archive_category(category_id):
    if not repository.is_admin():
        return
    category_row = project.get_category_data(category_id)
    if not category_row:
        return
    dir_name = get_category_path(category_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_category(category_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('domain', category_row['domain_id']))}/{category_row['name']}",
                                archive_file)
    return 1

def create_asset(name, category_id, inframe=100, outframe=220, preroll=0, postroll=0):
    if not tools.is_safe(name):
        return
    category_path = get_category_path(category_id)
    if not category_path:
        logger.error("Can't create asset")
        return
    dir_name = path_utils.clean_path(path_utils.join(category_path, name))
    asset_id = project.add_asset(name,
                                    category_id,
                                    inframe,
                                    outframe,
                                    preroll,
                                    postroll)
    if not asset_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_asset(asset_id)
        return
    asset_row = project.get_asset_data(asset_id)
    hooks.after_asset_creation_hook(asset_row['string'], name)
    events.add_creation_event('asset', asset_id)
    game.add_xps(game_vars._creation_xp_)
    game.add_coins(game._creation_coins_)
    return asset_id

def modify_asset_frame_range(asset_id, inframe, outframe, preroll, postroll):
    if project.modify_asset_frame_range(asset_id,
                                            inframe,
                                            outframe,
                                            preroll,
                                            postroll):
        logger.info("Frame range modified")
        return 1
    else:
        return

def archive_asset(asset_id):
    if not repository.is_admin():
        return
    asset_row = project.get_asset_data(asset_id)
    if not asset_row:
        return
    dir_name = get_asset_path(asset_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_asset(asset_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('category', asset_row['category_id']))}/{asset_row['name']}",
                                archive_file)
    return 1

def get_asset_data_from_work_env_id(work_env_id, column='*'):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    asset_id = project.get_stage_data(stage_id, 'asset_id')
    if not asset_id:
        return
    return project.get_asset_data(asset_id, column)

def get_stage_data_from_work_env_id(work_env_id, column='*'):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    return project.get_stage_data(stage_id, column)

def get_domain_data_from_work_env_id(work_env_id, column='*'):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    if not stage_id:
        return
    domain_id = project.get_stage_data(stage_id, 'domain_id')
    if not domain_id:
        return
    return project.get_domain_data(domain_id, column)

def create_stage(name, asset_id):
    category_id = project.get_asset_data(asset_id, 'category_id')
    if not category_id:
        return
    category_name = project.get_category_data(category_id, 'name')
    if not category_name:
        return
    domain_id = project.get_category_data(category_id, 'domain_id')
    if not domain_id:
        return
    domain_name = project.get_domain_data(domain_id, 'name')
    if not domain_name:
        return

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
    if not allowed:
        logger.warning(f"{name} doesn't match stages rules")
        return

    asset_path = get_asset_path(asset_id)
    if not asset_path:
        logger.error("Can't create stage")
        return
    dir_name = path_utils.clean_path(path_utils.join(asset_path, name))
    stage_id = project.add_stage(name, asset_id)
    if not stage_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_stage(stage_id)
        return
    stage_row = project.get_stage_data(stage_id)
    hooks.after_stage_creation_hook(string_stage = stage_row['string'],
                                    stage_name = name)
    variant_id = create_variant('main', stage_id, 'default variant')
    if variant_id:
        project.set_stage_default_variant(stage_id, variant_id)
    return stage_id

def archive_stage(stage_id):
    if not repository.is_admin():
        return
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return
    dir_name = get_stage_path(stage_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_stage(stage_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('asset', stage_row['asset_id']))}/{stage_row['name']}",
                                archive_file)
    return 1

def create_variant(name, stage_id, comment=''):
    if not tools.is_safe(name):
        return
    stage_path = get_stage_path(stage_id)
    if not stage_path:
        logger.error("Can't create variant")
        return
    dir_name = path_utils.clean_path(path_utils.join(stage_path, name))
    variant_id = project.add_variant(name, stage_id, comment)
    if not variant_id:
        return
    if not tools.create_folder(dir_name):
        project.remove_variant(variant_id)
        return
    tools.create_folder(path_utils.clean_path(path_utils.join(dir_name, '_EXPORTS')))
    tools.create_folder(path_utils.clean_path(path_utils.join(dir_name, '_SANDBOX')))
    tools.create_folder(path_utils.clean_path(path_utils.join(dir_name, '_VIDEOS')))
    variant_row = project.get_variant_data(variant_id)
    hooks.after_variant_creation_hook(variant_row['string'], name)
    events.add_creation_event('variant', variant_id)
    game.add_xps(game_vars._creation_xp_)
    return variant_id

def archive_variant(variant_id):
    if not repository.is_admin():
        return
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    dir_name = get_variant_path(variant_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file=''
    if not project.remove_variant(variant_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('stage', variant_row['stage_id']))}/{variant_row['name']}",
                                archive_file)
    return 1

def modify_stage_state(stage_id, state, comment=''):
    if state not in assets_vars._asset_states_list_:
        logger.warning(f"Unknown state {state}")
        return
    project.set_stage_data(stage_id, 'state', state)
    if comment is not None and comment != '':
        project.set_stage_data(stage_id, 'tracking_comment', comment)
    project.update_stage_progress(stage_id)
    asset_tracking.add_state_switch_event(stage_id, state, comment)
    if state == assets_vars._asset_state_done_:
        stage_row = project.get_stage_data(stage_id)
        amount = int((stage_row['work_time']/400)*game_vars._task_done_coins_)
        repository.add_user_coins(stage_row['assignment'], amount)
    return 1

def modify_stage_priority(stage_id, priority):
    if priority not in assets_vars._priority_list_:
        logger.warning(f"Unknown priority {priority}")
        return
    project.set_stage_data(stage_id, 'priority', priority)
    asset_tracking.add_priority_switch_event(stage_id, priority)
    return 1

def add_stage_comment(stage_id, comment):
    project.set_stage_data(stage_id, 'tracking_comment', comment)
    asset_tracking.add_comment_event(stage_id, comment)
    return 1

def edit_stage_note(stage_id, note):
    project.set_stage_data(stage_id, 'note', note)
    return 1

def modify_stage_assignment(stage_id, user_name):
    user_id = repository.get_user_row_by_name(user_name, 'id')
    if user_id not in project.get_users_ids_list():
        logger.warning(f"{user_name} never logged into project")
        return
    project.set_stage_data(stage_id, 'assignment', user_name)
    asset_tracking.add_assignment_event(stage_id, user_name)
    return 1

def modify_stage_estimation(stage_id, seconds):
    if type(seconds) != int:
        logger.warning(f'{seconds} is not a int')
        return
    project.set_stage_data(stage_id, 'estimated_time', seconds)
    project.update_stage_progress(stage_id)
    asset_tracking.add_estimation_event(stage_id, seconds)
    return 1

def add_work_time(work_env_id, work_time):
    project.add_work_time(work_env_id, work_time)
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    project.add_stage_work_time(stage_id, work_time)
    project.update_stage_progress(stage_id)
    asset_tracking.add_work_session_event(stage_id, work_time)
    amount = int((work_time/200)*game_vars._work_coins_)
    repository.add_user_coins(environment.get_user(), amount)
    return 1

def get_software_id_by_name(software):
    return project.get_software_data_by_name(software, 'id')

def create_work_env(software_id, variant_id):
    name = project.get_software_data(software_id, 'name')
    if not name:
        return
    if name not in project.get_softwares_names_list():
        logger.warning(f"{name} is not a valid work environment ( software not handled )")
        return
    variant_path = get_variant_path(variant_id)
    if not variant_path:
        logger.error("Can't create work env")
        return
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
    if not work_env_id:
        return
    if (not tools.create_folder(dir_name)) or (not tools.create_folder(screenshots_dir_name)) :
        project.remove_work_env(work_env_id)
        return
    work_env_row = project.get_work_env_data(work_env_id)
    hooks.after_work_environment_creation_hook(work_env_row['string'], name)
    add_version(work_env_id, do_screenshot=0, fresh=1)
    return work_env_id

def force_unlock(work_env_id):
    project.set_work_env_lock(work_env_id, 0, 1)
    return 1

def create_references_from_variant_id(work_env_id, variant_id):
    export_rows = project.get_variant_export_childs(variant_id)
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    stage = project.get_stage_data(stage_id, 'name')
    if not export_rows:
        return
    if stage in [assets_vars._modeling_, assets_vars._layout_]:
        export_rows = [export_rows[0]]
    at_least_one = False
    for export_row in export_rows:
        export_version_id = project.get_default_export_version(export_row['id'], 'id')
        if export_version_id:
            at_least_one = 1
            create_reference(work_env_id, export_version_id)
    if not at_least_one:
        logger.warning('No export found')
        return
    return

def create_reference(work_env_id,
                        export_version_id,
                        namespace_and_count=None,
                        auto_update=None):
    if auto_update is None:
        auto_update = user.user().get_reference_auto_update_default()
    if not namespace_and_count:
        namespace, count = numbered_namespace(work_env_id, export_version_id)
    else:
        namespace = namespace_and_count[0]
        count = namespace_and_count[1]
    reference_id = project.create_reference(work_env_id,
                                export_version_id,
                                namespace,
                                count,
                                int(auto_update))
    work_env_row = project.get_work_env_data(work_env_id)
    variant_row = project.get_variant_data(work_env_row['variant_id'])
    stage_name = project.get_stage_data(variant_row['stage_id'], 'name')
    reference_row = project.get_reference_data(reference_id)
    export_version_row = project.get_export_version_data(reference_row['export_version_id'])
    hooks.after_reference_hook(work_env_row['string'],
                                export_version_row['string'],
                                stage_name,
                                reference_row['stage'])
    return reference_id

def quick_reference(work_env_id, stage):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    stage_row = project.get_stage_data(variant_row['stage_id'])
    if not stage_row:
        return
    asset_row = project.get_asset_data(stage_row['asset_id'])
    if not asset_row:
        return
    stages_rows = project.get_asset_childs(asset_row['id'])
    for stage_row in stages_rows:
        if stage_row['name'] != stage:
            continue
        default_variant_id = stage_row['default_variant_id']
        default_variant_row = project.get_variant_data(default_variant_id)
        if len(project.get_export_versions_by_variant(default_variant_id, 'id')) == 0:
            logger.warning(f"No export found for {asset_row['name']}/{stage}/{default_variant_row['name']}")
            return
        return create_references_from_variant_id(work_env_id, default_variant_id)
    logger.warning(f"Stage {stage} not found for {asset_row['name']}")

def numbered_namespace(work_env_id, export_version_id, namespace_to_update=None):
    namespaces_list = project.get_references(work_env_id, 'namespace')
    if (namespace_to_update is not None) and namespace_to_update in namespaces_list:
        namespaces_list.remove(namespace_to_update)
    count = 0
    namespace_raw = build_namespace(export_version_id)
    namespace = f"{namespace_raw}"
    while namespace in namespaces_list:
        count+=1
        namespace = f"{namespace_raw}_{str(count)}"
    return namespace, count

'''
def modify_reference_variant(reference_id, variant_id):
    reference_row = project.get_reference_data(reference_id)
    old_variant_id = project.get_export_data(reference_row['export_id'], 'variant_id')
    if old_variant_id == variant_id:
        return
    exports_list = project.get_variant_export_childs(variant_id, 'id')
    if exports_list is None or exports_list == []:
        logger.warning("No export found")
        return
    export_id = exports_list[0]
    export_version_id = project.get_default_export_version(export_id, 'id')
    new_namespace, new_count = numbered_namespace(reference_row['work_env_id'], export_version_id, namespace_to_update=reference_row['namespace'])
    if export_version_id:
        project.update_reference_data(reference_id, ('export_id', export_id))
        project.update_reference_data(reference_id, ('export_version_id', export_version_id))
        if new_namespace != reference_row['namespace']:
            project.update_reference_data(reference_id, ('namespace', new_namespace))
        if new_count != reference_row['count']:
            project.update_reference_data(reference_id, ('count', new_count))
    return 1
'''

def remove_reference(reference_id):
    return project.remove_reference(reference_id)

def set_reference_last_version(reference_id):
    export_version_id = project.get_reference_data(reference_id, 'export_version_id')
    if export_version_id is None:
        return
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    default_export_version_id = project.get_default_export_version(export_row['id'], 'id')
    if not default_export_version_id:
        return
    if default_export_version_id == export_version_id:
        logger.info("Reference is up to date")
        return
    project.update_reference(reference_id, default_export_version_id)
    return 1

def modify_reference_LOD(work_env_id, LOD, namespaces_list):
    references_rows = project.get_references(work_env_id)
    for reference_row in references_rows:
        if reference_row['namespace'] not in namespaces_list:
            continue
        export_row = project.get_export_data(reference_row['export_id'])
        export_rows = project.get_variant_export_childs(export_row['variant_id'])
        for export_row in export_rows:
            if export_row['name'] != LOD:
                continue
            project.modify_reference_export(reference_row['id'], export_row['id'])
    return 1

def get_references_files(work_env_id):
    references_rows = project.get_references(work_env_id)
    references_dic = dict()
    for reference_row in references_rows:
        reference_files_list = json.loads(project.get_export_version_data(reference_row['export_version_id'],
                                                                            'files'))
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
            reference_files_list = json.loads(project.get_export_version_data(grouped_reference_row['export_version_id'],
                                                                                'files'))
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
    if not work_env_row:
        return
    variant_id = work_env_row['variant_id']
    return add_export_version(export_name,
                                files,
                                variant_id,
                                version_id,
                                comment,
                                execute_xp)

def add_export_version(export_name, files, variant_id, version_id, comment='', execute_xp=True, skip_temp_purge=False):
    variant_row = project.get_variant_data(variant_id)
    stage_name = project.get_stage_data(variant_row['stage_id'], 'name')
    extension_errors = []

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

    if (tools.get_files_list_size(files) > 5000000000) and (len(files)>3):
        logger.info(f"Files list size over 5Gb, starting files copying as subtask.")
        subtasks_library.threaded_copy(files, dir_name, max_threads=16)
        copied_files = []
    else:
        copied_files = tools.copy_files(files, dir_name)
        if copied_files is None:
            if not tools.remove_folder(dir_name):
                logger.warning(f"{dir_name} can't be removed, keep export version {new_version} in database")
            return
        if (len(copied_files) == len(files) and len(files) > 0) and not skip_temp_purge:
            tools.remove_tree(os.path.dirname(files[0]))
        elif len(copied_files) != len(files):
            logger.warning(f"Missing files, keeping temp dir: {os.path.dirname(files[0])}")
        else:
            pass

    export_version_id = project.add_export_version(new_version,
                                                    copied_files,
                                                    export_id,
                                                    version_id,
                                                    comment)
    game.add_xps(game_vars._export_xp_)
    game.add_coins(game_vars._export_coins_)
    if execute_xp:
        game.analyse_comment(comment, game_vars._export_penalty_)
    events.add_export_event(export_version_id)
    tags.analyse_comment(comment, 'export_version', export_version_id)
    export_version_string = instance_to_string(('export_version', export_version_id))
    hooks.after_export_hook(export_version_string=export_version_string,
                                export_dir=dir_name,
                                stage_name=stage_name)
    return export_version_id
        

def modify_export_version_comment(export_version_id, comment):
    if not project.modify_export_version_comment(export_version_id, comment):
        return
    tags.analyse_comment(comment, 'export_version', export_version_id)
    return 1

def modify_video_comment(video_id, comment):
    if not project.modify_video_comment(video_id, comment):
        return
    tags.analyse_comment(comment, 'video', video_id)
    return 1

def request_export(work_env_id, export_name, multiple=None, only_dir=None):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    export_id = get_or_add_export(export_name, variant_id)
    if not export_id:
        return
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
    if not work_env_id:
        return
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if not variant_id:
        return
    export_version_id = add_export_version(export_name, [], variant_id, version_id, comment)
    if not export_version_id:
        return
    export_version_path = get_export_version_path(export_version_id)
    return export_version_path

def archive_export(export_id):
    if not repository.is_admin():
        return
    export_row = project.get_export_data(export_id)
    if not export_row:
        return
    dir_name = get_export_path(export_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_export(export_id):
        return
    events.add_archive_event(f"Archived {instance_to_string(('variant', export_row['variant_id']))}/{export_row['name']}",
                                archive_file)
    return 1

def get_or_add_export(name, variant_id):
    if not tools.is_safe(name):
        return
    variant_path = get_variant_path(variant_id)
    if not variant_path:
        logger.error("Can't create export")
        return
    dir_name = path_utils.clean_path(path_utils.join(variant_path,
                                                        '_EXPORTS',
                                                        name))
    is_export = project.is_export(name, variant_id)
    if not is_export:
        export_id = project.add_export(name, variant_id)
        if not tools.create_folder(dir_name):
            project.remove_export(export_id)
            return
    else:
        export_id = project.get_export_by_name(name, variant_id)['id']
    return export_id

def archive_export_version(export_version_id):
    if not repository.is_admin():
        return
    export_version_row = project.get_export_version_data(export_version_id)
    export_id = export_version_row['export_id']
    if not export_version_row:
        return
    dir_name = get_export_version_path(export_version_id)
    if path_utils.isdir(dir_name):
        archive_file = tools.make_archive(dir_name)
        if archive_file:
            path_utils.rmtree(dir_name)
            logger.info(f"{dir_name} deleted")
    else:
        logger.warning(f"{dir_name} not found")
        archive_file = ''
    if not project.remove_export_version(export_version_id):
        return
    events.add_archive_event(f"Archived{instance_to_string(('export', export_version_row['export_id']))}/{export_version_row['name']}",
                                archive_file)
    if len(project.get_export_versions(export_id)) == 0:
        archive_export(export_id)
    return 1

def screen_over_version(version_id):
    version_row = project.get_version_data(version_id)
    if not version_row:
        return
    screenshot_file, thumbnail_file = image.screenshot(version_row['screenshot_path'],
                                                        version_row['thumbnail_path'])
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
    if not version_id:
        return
    version_row = project.get_version_data(version_id)
    hooks.after_work_version_creation_hook(version_row['string'], new_version, file_name)
    game.add_xps(game_vars._save_xp_)
    if analyse_comment and not fresh:
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
    if not video_id:
        return
    events.add_video_event(video_id, variant_id)
    game.add_xps(game_vars._video_xp_)
    tags.analyse_comment(comment, 'video', video_id)
    if analyse_comment:
        game.analyse_comment(comment, game_vars._video_penalty_)
    return video_id

def copy_work_version(work_version_id):
    clipboard_dic = dict()
    clipboard_dic['work_version_id'] = work_version_id
    clipboard.copy(json.dumps(clipboard_dic))
    logger.info("Version ID copied to clipboard")
    return 1

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
    return 1

def mirror_references(work_env_id, destination_work_env_id):
    for reference_id in project.get_references(destination_work_env_id, 'id'):
        remove_reference(reference_id)
    for reference_row in project.get_references(work_env_id):
        create_reference(destination_work_env_id,
                                reference_row['export_version_id'],
                                namespace_and_count=[reference_row['namespace'], reference_row['count']],
                                auto_update=reference_row['auto_update'])

def modify_version_comment(version_id, comment=''):
    if not project.modify_version_comment(version_id, comment):
        return
    tags.analyse_comment(comment, 'work_version', version_id)
    return 1

def set_asset_preview(asset_id, image_file):
    preview_file = None
    if image_file is not None:
        preview_path = path_utils.join(get_asset_path(asset_id), 'preview')
        if not path_utils.isdir(preview_path):
            path_utils.mkdir(preview_path)
        destination = path_utils.join(preview_path,
                        f"{project.get_asset_data(asset_id, 'name')}.jpg")
        preview_file = image.resize_preview(image_file, destination)
    return project.modify_asset_manual_preview(asset_id, preview_file)

def merge_file(file, work_env_id, comment="", do_screenshot=1):
    if not path_utils.isfile(file):
        logger.warning(f"{file} doesn't exists")
        return
    software_extension = project.get_software_data(project.get_work_env_data(work_env_id, 'software_id'),
                                                    'extension')
    file_extension = os.path.splitext(file)[-1].replace('.', '')
    if software_extension != file_extension:
        logger.warning(f"{file} doesn't match the work environment extension rules ( .ma )")
        return None
    version_id = add_version(work_env_id, comment, do_screenshot)
    version_row = project.get_version_data(version_id)
    path_utils.copyfile(file, version_row['file_path'])
    logger.info(f"{file} merged in new version {version_row['name']}")
    return version_id

def duplicate_version(version_id, work_env_id=None, comment=None):
    version_row = project.get_version_data(version_id)
    if not version_row:
        return
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
        path_utils.copyfile(version_row['screenshot_path'],
                                new_version_row['screenshot_path'])
    if path_utils.isfile(version_row['thumbnail_path']):
        path_utils.copyfile(version_row['thumbnail_path'],
                                new_version_row['thumbnail_path'])
    return new_version_id

def archive_version(version_id):
    if not repository.is_admin():
        return
    version_row = project.get_version_data(version_id)
    if version_row['name'] == '0001':
        logger.warning("You can't archive the default version (0001)")
        return
    if not version_row:
        return
    if path_utils.isfile(version_row['file_path']):
        zip_file = path_utils.join(os.path.split(version_row['file_path'])[0], 
                    'archives.zip')
        if tools.zip_files([version_row['file_path']], zip_file):
            path_utils.remove(version_row['file_path'])
            logger.info(f"{version_row['file_path']} deleted")
    else:
        logger.warning(f"{version_row['file_path']} not found")
    return project.remove_version(version_row['id'])

def archive_video(video_id):
    if not repository.is_admin():
        return
    video_row = project.get_video_data(video_id)
    if not video_row:
        return
    if path_utils.isfile(video_row['file_path']):
        zip_file = path_utils.join(os.path.split(video_row['file_path'])[0], 
                    'archives.zip')
        if tools.zip_files([video_row['file_path']], zip_file):
            path_utils.remove(video_row['file_path'])
            path_utils.remove(video_row['thumbnail_path'])
            logger.info(f"{video_row['file_path']} deleted")
    else:
        logger.warning(f"{video_row['file_path']} not found")
    return project.remove_video(video_row['id'])

def get_video_folder(version_id):
    version_row = project.get_version_data(version_id)
    work_env_path = get_work_env_path(version_row['work_env_id'])
    playblast_folder = path_utils.join(work_env_path, 'video')
    if not path_utils.isdir(playblast_folder):
        path_utils.mkdir(playblast_folder)
    return playblast_folder

def create_group(name, color='#798fe8'):
    if not tools.is_safe(name):
        return
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
    if not export_rows:
        return
    if stage == assets_vars._modeling_:
        export_rows = [export_rows[0]]
    for export_row in export_rows:
        export_version_id = project.get_default_export_version(export_row['id'], 'id')
        if export_version_id:
            create_grouped_reference(group_id, export_version_id)
    return 1

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
    export_version_id = project.get_grouped_reference_data(grouped_reference_id,
                                                            'export_version_id')
    if not export_version_id:
        return
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    default_export_version_id = project.get_default_export_version(export_row['id'], 'id')
    if not default_export_version_id:
        logger.info("Grouped reference is up to date")
        return
    if default_export_version_id == export_version_id:
        return
    project.update_grouped_reference(grouped_reference_id, default_export_version_id)
    return 1

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
    if not project.add_asset_tracking_event(stage_id, event_type, data, comment):
        return
    tags.analyse_comment(comment, 'stage', stage_id)
    return 1

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
    domain_name = project.get_domain_data(domain_id, 'name')
    if not domain_name:
        return
    return path_utils.join(environment.get_project_path(), domain_name)

def get_category_path(category_id):
    category_row = project.get_category_data(category_id)
    if not category_row:
        return
    category_name = category_row['name']
    domain_path = get_domain_path(category_row['domain_id'])
    if not domain_path:
        return
    return path_utils.join(domain_path, category_name)

def get_asset_path(asset_id):
    asset_row = project.get_asset_data(asset_id)
    if not asset_row:
        return
    asset_name = asset_row['name']
    category_path = get_category_path(asset_row['category_id'])
    if not category_path:
        return
    return path_utils.join(category_path, asset_name)

def get_stage_path(stage_id):
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return
    stage_name = stage_row['name']
    asset_path = get_asset_path(stage_row['asset_id'])
    if not asset_path:
        return
    return path_utils.join(asset_path, stage_name)

def get_variant_path(variant_id):
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    variant_name = variant_row['name']
    stage_path = get_stage_path(variant_row['stage_id'])
    if not stage_path:
        return
    return path_utils.join(stage_path, variant_name)

def get_variant_export_path(variant_id):
    variant_row = project.get_variant_data(variant_id)
    if not variant_row:
        return
    variant_name = variant_row['name']
    stage_path = get_stage_path(variant_row['stage_id'])
    if not stage_path:
        return
    return path_utils.join(stage_path, variant_name, '_EXPORTS')

def get_work_env_path(work_env_id):
    work_env_row = project.get_work_env_data(work_env_id)
    if not work_env_row:
        return
    work_env_name = work_env_row['name']
    variant_path = get_variant_path(work_env_row['variant_id'])
    if not variant_path:
        return
    return path_utils.join(variant_path, work_env_name)

def get_video_path(variant_id):
    variant_path = get_variant_path(variant_id)
    if not variant_path:
        return
    dir_name = path_utils.join(variant_path, '_VIDEOS')
    if not path_utils.isdir(dir_name):
        path_utils.mkdir(dir_name)
    return dir_name

def get_export_path(export_id):
    export_row = project.get_export_data(export_id)
    if not export_row:
        return
    export_name = export_row['name']
    variant_path = get_variant_path(export_row['variant_id'])
    if not variant_path:
        return
    return path_utils.join(variant_path,
                            '_EXPORTS',
                            export_name)

def get_temp_export_path(export_id):
    local_path = user.user().get_local_path()
    project_path = environment.get_project_path()
    if local_path is None or local_path == '':
        dir_name = tools.temp_dir()
        logger.warning("Your local path is not setted, exporting in default temp dir.")
        return dir_name
    export_row = project.get_export_data(export_id)
    if not export_row:
        return
    export_name = export_row['name']
    variant_path = get_variant_path(export_row['variant_id'])
    if not variant_path:
        return
    dir_name = path_utils.join(variant_path, '_EXPORTS', export_name, 'temp')
    dir_name = local_path+dir_name[len(project_path):]
    return dir_name

def get_temp_video_path(variant_id):
    local_path = user.user().get_local_path()
    project_path = environment.get_project_path()
    if local_path is None or local_path == '':
        dir_name = tools.temp_dir()
        logger.warning("Your local path is not setted, exporting in default temp dir.")
        return dir_name
    video_path = get_video_path(variant_id)
    if not video_path:
        return
    dir_name = path_utils.join(video_path, 'temp')
    dir_name = local_path+dir_name[len(project_path):]
    if not path_utils.isdir(dir_name):
        path_utils.makedirs(dir_name)
    dir_name = tools.temp_dir_in_dir(dir_name)
    return dir_name

def get_export_version_path(export_version_id):
    export_version_row = project.get_export_version_data(export_version_id)
    if not export_version_row:
        return
    export_version_name = export_version_row['name']
    export_path = get_export_path(export_version_row['export_id'])
    if not export_path:
        return
    return path_utils.join(export_path, export_version_name)

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
    if not work_env_row['export_extension']:
        extension = project.get_default_extension(stage_row['name'], work_env_row['software_id'])
    else:
        extension = work_env_row['export_extension']

    if not extension:
        logger.error("Can't build file name")
        return
    file_name = f"{category_row['name']}"
    file_name += f"_{asset_row['name']}"
    file_name += f"_{stage_row['name']}"
    file_name += f"_{variant_row['name']}"
    file_name += f"_{export_name}"
    if multiple:
        file_name += f".{multiple}"
    file_name += f".{extension}"
    return file_name

def build_namespace(export_version_id):
    export_version_row = project.get_export_version_data(export_version_id)
    export_row = project.get_export_data(export_version_row['export_id'])
    variant_row = project.get_variant_data(export_row['variant_id'])
    stage_row = project.get_stage_data(variant_row['stage_id'])
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    domain_row = project.get_domain_data(category_row['domain_id'])
    if domain_row['name'] == 'assets':
        namespace = f"{category_row['name'][:5]}" 
    else:
        namespace = f"{category_row['name']}" 
    namespace += f"_{asset_row['name']}" 
    if stage_row['name'] == 'animation' or stage_row['name'] == 'cfx':
        namespace += f"_{export_row['name']}"
    namespace += f"_{stage_row['name'][:3]}"
    namespace += f"_{variant_row['name']}"
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
    instances_list = string.split('/')
    if len(instances_list) == 6:
        instance_type = 'work_env'
        instance_id = project.get_work_env_data_by_string(string, 'id')
    elif len(instances_list) == 7:
        instance_type = 'work_version'
        instance_id = project.get_work_version_data_by_string(string, 'id')
    else:
        logger.warning('The given string is not a work instance')
        return (None, None)
    return (instance_type, instance_id)

def string_to_export_instance(string):
    instances_list = string.split('/')
    if len(instances_list) == 6:
        instance_type = 'export'
        instance_id = project.get_export_data_by_string(string, 'id')
    elif len(instances_list) == 7:
        instance_type = 'export_version'
        instance_id = project.get_export_version_data_by_string(string, 'id')
    else:
        logger.warning('The given string is not an export instance')
        return (None, None)
    return (instance_type, instance_id)