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

# This module permits to access the wizard
# core with simplified commands

# Python modules
import logging

# Wizard modules
from wizard import core
from wizard import vars
from wizard import gui
logger = logging.getLogger(__name__)

class repository:
    def __init__(self):
        pass

    def projects(self):
        # Return a list of the existing projects in the repository database
        return core.repository.get_projects_names_list()

    def create_project(self, project_name,
                            project_path,
                            project_password,
                            frame_rate=24,
                            image_format=[1920,1080]
                            ):
        return core.create_project.create_project(project_name,
                            project_path,
                            project_password,
                            frame_rate,
                            image_format
                            )

    def users(self):
        # Return a list of the existing users in the repository database
        return core.repository.get_user_names_list()

    def flush_ips(self):
        return core.repository.flush_ips()

    def create_user(self, user_name, user_password, email, administrator_pass=''):
        return core.repository.create_user(user_name,
                                            user_password,
                                            email,
                                            administrator_pass)

    def upgrade_user_privilege(self, user_name, administrator_pass):
        return core.repository.upgrade_user_privilege(user_name,
                                                        administrator_pass)

    def downgrade_user_privilege(self, user_name, administrator_pass):
        return core.repository.downgrade_user_privilege(user_name,
                                                        administrator_pass)

class user:
    def __init__(self):
        pass

    def set(self, user_name, password):
        # Log a user
        if core.user.log_user(user_name, password):
            gui.gui_server.restart_ui()

    def get(self):
        # Return the current user
        return core.environment.get_user()

    def change_password(self, old_password, new_password):
        return core.repository.modify_user_password(core.environment.get_user(),
                                                    old_password,
                                                    new_password)

    def is_admin(self):
        # Return the current user privilege
        return core.repository.is_admin()

    def set_team_dns(self, host, port):
        # Set the team server DNS as user preference
        return core.user.user().set_team_dns(host, port)

    def get_team_dns(self):
        # Return the current team server DNS
        return core.environment.get_team_dns()

    def set_popups_settings(self, enabled=1, duration=3, keep_until_comment=True):
        # Set the given popups settings for the current user
        return core.user.user().set_popups_settings(enabled, duration, keep_until_comment)

class project:
    def __init__(self):
        pass

    def set(self, project_name, project_password):
        # Log a project
        if core.user.log_project(project_name, project_password):
            gui.gui_server.restart_ui()

    def name(self):
        # Return the current project name
        return core.environment.get_project_name()

    def path(self):
        # Return the current project path
        return core.environment.get_project_path()

    def change_password(self, old_password, new_password, administrator_pass):
        return core.repository.modify_project_password(core.environment.get_project_name(),
                                                    old_password,
                                                    new_password,
                                                    administrator_pass)

    def set_software_executable(self, software_name, executable_path):
        software_id = core.project.get_software_data_by_name(software_name, 'id')
        if software_id:
            core.project.set_software_path(software_id, executable_path)

    def set_software_batch_executable(self, software_name, batch_executable_path):
        software_id = core.project.get_software_data_by_name(software_name, 'id')
        if software_id:
            core.project.set_software_batch_path(software_id, batch_executable_path)

class shelf:
    def __init__(self):
        pass

    def create_shelf_tool(self, name, script, help, only_subprocess=0, icon=vars.ressources._default_script_shelf_icon_):
        # Create a shelf tool with the given arguments
        return core.shelf.create_project_script(name, script, help, only_subprocess, icon)

    def create_separator(self):
        # Create a shelf separator
        return core.shelf.create_separator()

class assets:
    def __init__(self):
        pass

    # Creation commands

    def create_sequence(self, name):
        string_sequence = None
        sequence_id = core.assets.create_category(name, 3)
        if sequence_id:
            string_sequence = core.assets.instance_to_string(('category',
                                                                sequence_id))
        return string_sequence

    def create_asset(self, parent, name):
        # The parent argument should look like
        # "assets/characters"
        string_asset = None

        if type(parent) == str:
            instance_type, category_id = core.assets.string_to_instance(parent)
        else:
            category_id = parent

        if category_id:
            asset_id = core.assets.create_asset(name, category_id)
            if asset_id:
                string_asset = core.assets.instance_to_string(('asset',
                                                                asset_id))
        return string_asset

    def create_stage(self, parent, stage):
        # The parent argument should look like
        # "assets/characters/Joe"
        string_stage = None

        if type(parent) == str:
            instance_type, asset_id = core.assets.string_to_instance(parent)
        else:
            asset_id = parent

        if asset_id:
            stage_id = core.assets.create_stage(stage, asset_id)
            if stage_id:
                string_stage = core.assets.instance_to_string(('stage',
                                                                stage_id))
        return string_stage

    def create_variant(self, parent, name):
        # The parent argument should look like
        # "assets/characters/Joe/modeling"
        string_variant = None

        if type(parent) == str:
            instance_type, stage_id = core.assets.string_to_instance(parent)
        else:
            stage_id = parent

        if stage_id:
            variant_id = core.assets.create_variant(name, stage_id)
            if variant_id:
                string_variant = core.assets.instance_to_string(('variant',
                                                                    variant_id))
        return string_variant

    def create_work_env(self, parent, software):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main"
        string_work_env = None

        if type(parent) == str:
            instance_type, variant_id = core.assets.string_to_instance(parent)
        else:
            variant_id = parent

        if variant_id:
            software_id = core.assets.get_software_id_by_name(software)
            if software_id:
                work_env_id = core.assets.create_work_env(software_id, variant_id)
                if work_env_id:
                    string_work_env = core.assets.instance_to_string(('work_env',
                                                                        work_env_id))
        return string_work_env

    # Exports commands

    def create_export(self, variant, export_name, files_list, comment=''):
        # Create a new export in the given variant and export name and merge the given files list.
        success = None

        if type(variant) == str:
            instance_type, variant_id = core.assets.string_to_instance(variant)
        else:
            variant_id = variant

        if variant_id and instance_type == 'variant':
            success = core.assets.merge_file_as_export_version(export_name, files_list, variant_id, comment)
        return success

    def batch_export(self, work_env, namespaces_list=[], rolls=False, custom_frame_range=None, refresh_assets_in_scene=False):
        
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id and instance_type == 'work_env':
            version_id = core.project.get_last_work_version(work_env_id, 'id')
            if version_id:
                version_id = version_id[0]
                stage = core.assets.get_stage_data_from_work_env_id(work_env_id, 'name')
                asset_row = core.assets.get_asset_data_from_work_env_id(work_env_id)
                if not custom_frame_range:
                    frange = [asset_row['inframe'], asset_row['outframe']]
                else:
                    frange = custom_frame_range
                if rolls:
                    frange[0] = frange[0]-asset_row['preroll']
                    frange[1] = frange[1]+asset_row['postroll']

                settings_dic = dict()
                settings_dic['batch_type'] = 'export'
                settings_dic['frange'] = frange
                settings_dic['refresh_assets'] = refresh_assets_in_scene
                settings_dic['nspace_list'] = namespaces_list
                settings_dic['stage_to_export'] = stage
                core.subtasks_library.batch_export(version_id, settings_dic)

    def batch_export_camera(self, work_env, namespaces_list=[], rolls=False, custom_frame_range=None, refresh_assets_in_scene=False):

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id and instance_type == 'work_env':
            version_id = core.project.get_last_work_version(work_env_id, 'id')
            if version_id:
                version_id = version_id[0]
                #stage = core.assets.get_stage_data_from_work_env_id(work_env_id, 'name')
                asset_row = core.assets.get_asset_data_from_work_env_id(work_env_id)
                if not custom_frame_range:
                    frange = [asset_row['inframe'], asset_row['outframe']]
                else:
                    frange = custom_frame_range
                if rolls:
                    frange[0] = frange[0]-asset_row['preroll']
                    frange[1] = frange[1]+asset_row['postroll']

                settings_dic = dict()
                settings_dic['batch_type'] = 'export'
                settings_dic['frange'] = frange
                settings_dic['refresh_assets'] = refresh_assets_in_scene
                settings_dic['nspace_list'] = namespaces_list
                settings_dic['stage_to_export'] = 'camera'
                core.subtasks_library.batch_export(version_id, settings_dic)

    # Group commands

    def create_group(self, name):
        # Create a new group with the given name
        return core.assets.create_group(name)

    def modify_group_color(self, group, color):
        # Modify the given group color with the given color
        success = None

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            success = core.project.modify_group_color(group_id, color)
        return success

    def delete_group(self, group):
        # Delete the given group
        success = None

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            success = core.assets.remove_group(group_id)
        return success

    # References commands

    def create_reference(self, destination_work_env, variant_to_reference):
        # Reference the given variant in the given work env
        new_references = None

        if type(destination_work_env) == str:
            dest_instance_type, work_env_id = core.assets.string_to_work_instance(destination_work_env)
        else:
            work_env_id = destination_work_env

        if type(variant_to_reference) == str:
            orig_instance_type, variant_id = core.assets.string_to_instance(variant_to_reference)
        else:
            variant_id = variant_to_reference

        if work_env_id and variant_id:
            old_references = core.project.get_references(work_env_id, 'namespace')
            core.assets.create_references_from_variant_id(work_env_id, variant_id)
            new_references = list(set(core.project.get_references(work_env_id, 'namespace')) - set(old_references))
        return new_references

    def create_grouped_reference(self, destination_group, variant_to_reference):
        # Reference the given variant in the given group
        new_references = None

        if type(destination_group) == str:
            group_id = core.project.get_group_by_name(destination_group, 'id')
        else:
            group_id = destination_group

        if type(variant_to_reference) == str:
            orig_instance_type, variant_id = core.assets.string_to_instance(variant_to_reference)
        else:
            variant_id = variant_to_reference

        if group_id and variant_id:
            old_references = core.project.get_grouped_references(group_id, 'namespace')
            core.assets.create_grouped_references_from_variant_id(group_id, variant_id)
            new_references = list(set(core.project.get_grouped_references(group_id, 'namespace')) - set(old_references))
        return new_references

    def create_referenced_group(self, destination_work_env, group):
        # Reference the given group in the given destination work environment

        if type(destination_work_env) == str:
            dest_instance_type, work_env_id = core.assets.string_to_work_instance(destination_work_env)
        else:
            work_env_id = destination_work_env

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if work_env_id and group_id:
            core.assets.create_referenced_group(work_env_id, group_id)

    def get_references(self, work_env):
        # Return the work environment references as a list of namespaces

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            return core.project.get_references(work_env_id, 'namespace')
        else:
            return None

    def get_references_from_group(self, group):
        # Return the group references as a list of namespaces

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            return core.project.get_grouped_references(group_id, 'namespace')
        else:
            return None

    def get_referenced_groups(self, work_env):
        # Return the work environment referenced groups as a list of namespaces

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            return core.project.get_referenced_groups(work_env_id, 'namespace')
        else:
            return None

    def remove_reference(self, work_env, reference):
        # Remove the given reference from the work environment

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(work_env_id, reference, 'id')
            if reference_id:
                return core.assets.remove_reference(reference_id)

    def remove_reference_from_group(self, group, reference):
        # Remove the given reference from the group

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(group_id, reference, 'id')
            if grouped_reference_id:
                return core.assets.remove_grouped_reference(grouped_reference_id)

    def remove_referenced_group(self, work_env, referenced_group):
        # Remove the given referenced group from the work environment

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            referenced_group_id = core.project.get_referenced_group_by_namespace(work_env_id, referenced_group, 'id')
            if referenced_group_id:
                return core.assets.remove_referenced_group(referenced_group_id)

    def set_reference_as_default(self, work_env, reference):
        # Modify the given reference to match the default export version

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(work_env_id, reference, 'id')
            if reference_id:
                return core.assets.set_reference_last_version(reference_id)

    def set_grouped_reference_as_default(self, group, reference):
        # Modify the given reference to match the default export version

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(group_id, reference, 'id')
            if grouped_reference_id:
                return core.assets.set_grouped_reference_last_version(grouped_reference_id)

    def modify_reference_auto_update(self, work_env, reference, auto_update=True):
        # Modify the auto update option of the given reference
        if auto_update:
            auto_update = 1
        else:
            auto_update = 0

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(work_env_id, reference, 'id')
            if reference_id:
                return core.project.modify_reference_auto_update(reference_id, auto_update)

    def modify_grouped_reference_auto_update(self, group, reference, auto_update=True):
        # Modify the auto update option of the given reference
        if auto_update:
            auto_update = 1
        else:
            auto_update = 0

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(group_id, reference, 'id')
            if grouped_reference_id:
                return core.project.modify_grouped_reference_auto_update(grouped_reference_id, auto_update)

    # Archive commands

    def archive_asset(self, asset):
        success = None

        if type(asset) == str:
            instance_type, asset_id = core.assets.string_to_instance(asset)
        else:
            asset_id = asset

        if asset_id:
            success = core.assets.archive_asset(asset_id)
        return success

    def archive_sequence(self, sequence):
        success = None

        if type(sequence) == str:
            instance_type, sequence_id = core.assets.string_to_instance(sequence)
        else:
            sequence_id = sequence

        if sequence_id:
            success = core.assets.archive_category(sequence_id)
        return success

    def archive_stage(self, stage):
        success = None

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            success = core.assets.archive_stage(stage_id)
        return success

    def archive_variant(self, variant):
        success = None

        if type(variant) == str:
            instance_type, variant_id = core.assets.string_to_instance(variant)
        else:
            variant_id = variant

        if variant_id:
            success = core.assets.archive_variant(variant_id)
        return success

    def archive_work_env(self, work_env):
        success = None

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            instance_type = 'work_env'
            work_env_id = work_env

        if instance_type == 'work_env' and work_env_id:
            success = core.assets.archive_work_env(work_env_id)
        return success

    def archive_work_version(self, work_version):
        success = None

        if type(work_version) == str:
            instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
        else:
            instance_type = 'work_version'
            work_version_id = work_version

        if instance_type == 'work_version' and work_version_id:
            success = core.assets.archive_work_version(work_version_id)
        return success

    # List commands

    def list_domains(self, column='*'):
        domains = core.project.get_domains(column)
        return domains

    def list_categories(self, parent, column='*'):
        # The parent argument should look like
        # "assets"
        categories = None

        if type(parent) == str:
            instance_type, domain_id = core.assets.string_to_instance(parent)
        else:
            domain_id = parent

        if domain_id:
            categories = core.project.get_domain_childs(domain_id, column)
        return categories

    def list_assets(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters"
        assets = None

        if type(parent) == str:
            instance_type, category_id = core.assets.string_to_instance(parent)
        else:
            category_id = parent

        if category_id:
            assets = core.project.get_category_childs(category_id, column)
        return assets

    def list_stages(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters/Joe"
        stages = None

        if type(parent) == str:
            instance_type, asset_id = core.assets.string_to_instance(parent)
        else:
            asset_id = parent

        if asset_id:
            stages = core.project.get_asset_childs(asset_id, column)
        return stages

    def list_variants(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters/Joe/modeling"
        variants = None

        if type(parent) == str:
            instance_type, stage_id = core.assets.string_to_instance(parent)
        else:
            stage_id = parent

        if stage_id:
            variants = core.project.get_stage_childs(stage_id, column)
        return variants

    def list_work_envs(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main"
        work_envs = None

        if type(parent) == str:
            instance_type, variant_id = core.assets.string_to_instance(parent)
        else:
            variant_id = parent

        if variant_id:
            work_envs = core.project.get_variant_work_envs_childs(variant_id, column)
        return work_envs

    def list_work_versions(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main/blender"
        work_versions = None

        if type(parent) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(parent)
        else:
            work_env_id = parent

        if work_env_id:
            work_versions = core.project.get_work_versions(work_env_id, column)
        return work_versions

    def list_exports(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main/"
        exports = None

        if type(parent) == str:
            instance_type, variant_id = core.assets.string_to_instance(parent)
        else:
            variant_id = parent

        if variant_id:
            exports = core.project.get_variant_export_childs(variant_id, column)
        return exports

    def list_export_versions(self, parent, column='*'):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main/LOD1"

        export_versions = None

        if type(parent) == str:
            instance_type, export_id = core.assets.string_to_export_instance(parent)
        else:
            export_id = parent

        if export_id:
            export_versions = core.project.get_export_childs(export_id, column)
        return export_versions

class tracking:
    def __init__(self):
        pass

    def get_task_assignment(self, stage):

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'assignment')

    def get_task_state(self, stage):

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'state')

    def get_task_work_time(self, stage):
        
        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'work_time')

    def get_task_estimated_time(self, stage):
        
        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'estimated_time')

    def assign_task(self, stage, user):
        user_id = core.repository.get_user_row_by_name(user, 'id')

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if user_id and stage_id:
            core.assets.modify_stage_assignment(stage_id, user)

    def set_task_state(self, stage, state, comment=''):
        
        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            core.assets.modify_stage_state(stage_id, state, comment)

    def estimate_task_time(self, stage, time):
        
        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            core.assets.modify_stage_estimation(stage_id, time)    

    def add_task_comment(self, stage, comment):
        
        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            core.assets.add_stage_comment(stage_id, comment)    

class launch:
    def __init__(self):
        pass

    def work_env(self, work_env):
        # Run the last version of the given work environment related software

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            last_work_version_id = core.project.get_last_work_version(work_env_id, 'id')
            if last_work_version_id:
                core.launch.launch_work_version(last_work_version_id[0])

    def work_version(self, work_version):
        # Run the given work version related software

        if type(work_version) == str:
            instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
        else:
            work_version_id = work_version

        if work_version_id:
            core.launch.launch_work_version(work_version_id)

    def kill_work_env(self, work_env):
        # Terminate the given work environment related software instance

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            core.launch.kill(work_env_id)

    def kill_all(self):
        # Terminate all the running work environments
        core.launch.kill_all()

    def get_running_work_envs(self):
        # Return the running work environments related softwares instances
        running_work_envs = []
        running_work_env_ids = core.launch.get()
        if running_work_env_ids:
            for work_env_id in running_work_env_ids:
                running_work_envs.append(core.assets.instance_to_string(('work_env',
                                                                            work_env_id)))
        return running_work_envs

    def lock_work_env(self, work_env):
        # Lock the given work environment for the current user

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            core.project.set_work_env_lock(work_env_id, 1)

    def unlock_work_env(self, work_env):
        # Unlock the given work environment if it is locked by the current user
        
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            core.project.set_work_env_lock(work_env_id, 0)

    def unlock_all(self):
        # Unlock all the work environments locked by the current user
        core.project.unlock_all()

class team:
    def __init__(self):
        pass

    def refresh_ui(self):
        # Refresh the project team interfaces
        if core.user.user().get_team_dns():
            core.team_client.refresh_team(core.environment.get_team_dns())

    def set_team_DNS(self, host, port):
        # Set a team server DNS for wizard
        core.user.user().set_team_dns(host, port)

    def get_team_dns(self):
        # Return the setted wizard team DNS
        if core.user.user().get_team_dns():
            return core.environment.get_team_dns()
        else:
            return None

class ui:
    def __init__(self):
        pass

    def is_gui(self):
        # Return true if the wizard gui is openned
        # False if it is PyWizard or Wizard_CMD
        return core.environment.is_gui()

    def raise_ui(self):
        # Raise the wizard window
        gui.gui_server.raise_ui()

    def restart_ui(self):
        # Restart wizard
        gui.gui_server.restart_ui()

    def refresh_ui(self):
        # Refresh the interface
        gui.gui_server.refresh_ui()

    def focus_asset(self, asset):
        # Focus on the given asset in the project tree

        if type(asset) == str:
            instance_type, instance_id = core.assets.string_to_instance(asset)
        else:
            instance_type = 'asset'
            instance_id = asset

        if instance_type == 'asset':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_stage(self, stage):
        # Focus on the given stage in the project tree

        if type(stage) == str:
            instance_type, instance_id = core.assets.string_to_instance(stage)
        else:
            instance_type = 'stage'
            instance_id = stage

        if instance_type == 'stage':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_variant(self, variant):
        # Focus on the given variant in wizard

        if type(variant) == str:
            instance_type, instance_id = core.assets.string_to_instance(variant)
        else:
            instance_type = 'variant'
            instance_id = variant

        if instance_type == 'variant':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_work_version(self, work_version):
        # Focus on the given work version in the work versions tab

        if type(work_version) == str:
            instance_type, instance_id = core.assets.string_to_work_instance(work_version)
        else:
            instance_type = 'work_version'
            instance_id = work_version

        if instance_type == 'work_version':
            gui.gui_server.focus_work_version(instance_id)

repository = repository()
user = user()
project = project()
shelf = shelf()
assets = assets()
tracking = tracking()
launch = launch()
team = team()
ui = ui()
