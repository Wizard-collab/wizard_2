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
from wizard import gui
logger = logging.getLogger(__name__)

class site:
    def __init__(self):
        pass

    def projects(self):
        # Return a list of the existing projects in the site database
        return core.site.get_projects_names_list()

    def users(self):
        # Return a list of the existing users in the site database
        return core.site.get_user_names_list()

    def upgrade_user_privilege(self, user_name, administrator_pass):
        return core.site.upgrade_user_privilege(user_name,
                                                        administrator_pass)

    def downgrade_user_privilege(self, user_name, administrator_pass):
        return core.site.downgrade_user_privilege(user_name,
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
        return core.site.modify_user_password(core.environment.get_user(),
                                                    old_password,
                                                    new_password)

    def is_admin(self):
        # Return the current user privilege
        return core.site.is_admin()

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
        instance_type, category_id = core.assets.string_to_instance(parent)
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
        instance_type, asset_id = core.assets.string_to_instance(parent)
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
        instance_type, stage_id = core.assets.string_to_instance(parent)
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
        instance_type, variant_id = core.assets.string_to_instance(parent)
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
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id and instance_type == 'variant':
            success = core.assets.merge_file_as_export_version(export_name, files_list, variant_id, comment)
        return success

    def batch_export(self, work_env, namespaces_list=[], rolls=False, custom_frame_range=None, refresh_assets_in_scene=False):
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
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
                settings_dic['frange'] = frange
                settings_dic['refresh_assets'] = refresh_assets_in_scene
                settings_dic['nspace_list'] = namespaces_list
                settings_dic['stage_to_export'] = stage
                core.subtasks_library.batch_export(version_id, settings_dic)

    def batch_export_camera(self, work_env, namespaces_list=[], rolls=False, custom_frame_range=None, refresh_assets_in_scene=False):
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
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
                settings_dic['frange'] = frange
                settings_dic['refresh_assets'] = refresh_assets_in_scene
                settings_dic['nspace_list'] = namespaces_list
                settings_dic['stage_to_export'] = 'camera'
                core.subtasks_library.batch_export(version_id, settings_dic)

    # Group commands

    def create_group(self, name):
        # Create a new group with the given name
        return core.assets.create_group(name)

    def modify_group_color(self, group_name, color):
        # Modify the given group color with the given color
        success = None
        group_id = core.project.get_group_by_name(group_name, 'id')
        if group_id:
            success = core.project.modify_group_color(group_id, color)
        return success

    def delete_group(self, group_name):
        # Delete the given group
        success = None
        group_id = core.project.get_group_by_name(group_name, 'id')
        if group_id:
            success = core.assets.remove_group(group_id)
        return success

    # References commands

    def create_reference(self, destination_work_env, variant_to_reference):
        # Reference the given variant in the given work env
        new_references = None
        dest_instance_type, work_env_id = core.assets.string_to_work_instance(destination_work_env)
        orig_instance_type, variant_id = core.assets.string_to_instance(variant_to_reference)
        if work_env_id and variant_id:
            old_references = core.project.get_references(work_env_id, 'namespace')
            core.assets.create_references_from_variant_id(work_env_id, variant_id)
            new_references = list(set(core.project.get_references(work_env_id, 'namespace')) - set(old_references))
        return new_references

    def create_grouped_reference(self, destination_group, variant_to_reference):
        # Reference the given variant in the given group
        new_references = None
        group_id = core.project.get_group_by_name(destination_group, 'id')
        orig_instance_type, variant_id = core.assets.string_to_instance(variant_to_reference)
        if group_id and variant_id:
            old_references = core.project.get_grouped_references(group_id, 'namespace')
            core.assets.create_grouped_references_from_variant_id(group_id, variant_id)
            new_references = list(set(core.project.get_grouped_references(group_id, 'namespace')) - set(old_references))
        return new_references

    def create_referenced_group(self, destination_work_env, group):
        # Reference the given group in the given destination work environment
        dest_instance_type, work_env_id = core.assets.string_to_work_instance(destination_work_env)
        group_id = core.project.get_group_by_name(group, 'id')
        if work_env_id and group_id:
            core.assets.create_referenced_group(work_env_id, group_id)

    def get_references(self, work_env):
        # Return the work environment references as a list of namespaces
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            return core.project.get_references(work_env_id, 'namespace')
        else:
            return None

    def get_references_from_group(self, group):
        # Return the group references as a list of namespaces
        group_id = core.project.get_group_by_name(group, 'id')
        if group_id:
            return core.project.get_grouped_references(group_id, 'namespace')
        else:
            return None

    def get_referenced_groups(self, work_env):
        # Return the work environment referenced groups as a list of namespaces
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            return core.project.get_referenced_groups(work_env_id, 'namespace')
        else:
            return None

    def remove_reference(self, work_env, reference):
        # Remove the given reference from the work environment
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(work_env_id, reference, 'id')
            if reference_id:
                return core.assets.remove_reference(reference_id)

    def remove_reference_from_group(self, group, reference):
        # Remove the given reference from the group
        group_id = core.project.get_group_by_name(group, 'id')
        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(group_id, reference, 'id')
            if grouped_reference_id:
                return core.assets.remove_grouped_reference(grouped_reference_id)

    def remove_referenced_group(self, work_env, referenced_group):
        # Remove the given referenced group from the work environment
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            referenced_group_id = core.project.get_referenced_group_by_namespace(work_env_id, referenced_group, 'id')
            if referenced_group_id:
                return core.assets.remove_referenced_group(referenced_group_id)

    def set_reference_as_default(self, work_env, reference):
        # Modify the given reference to match the default export version
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(work_env_id, reference, 'id')
            if reference_id:
                return core.assets.set_reference_last_version(reference_id)

    def set_grouped_reference_as_default(self, group, reference):
        # Modify the given reference to match the default export version
        group_id = core.project.get_group_by_name(group, 'id')
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
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
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
        group_id = core.project.get_group_by_name(group, 'id')
        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(group_id, reference, 'id')
            if grouped_reference_id:
                return core.project.modify_grouped_reference_auto_update(grouped_reference_id, auto_update)

    # Archive commands

    def archive_asset(self, asset):
        success = None
        instance_type, asset_id = core.assets.string_to_instance(asset)
        if asset_id:
            success = core.assets.archive_asset(asset_id)
        return success

    def archive_sequence(self, sequence):
        success = None
        instance_type, sequence_id = core.assets.string_to_instance(sequence)
        if sequence_id:
            success = core.assets.archive_category(sequence_id)
        return success

    def archive_stage(self, stage):
        success = None
        instance_type, stage_id = core.assets.string_to_instance(stage)
        if stage_id:
            success = core.assets.archive_stage(stage_id)
        return success

    def archive_variant(self, variant):
        success = None
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            success = core.assets.archive_variant(variant_id)
        return success

    def archive_work_env(self, work_env):
        success = None
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if instance_type == 'work_env' and work_env_id:
            success = core.assets.archive_work_env(work_env_id)
        return success

    def archive_work_version(self, work_version):
        success = None
        instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
        if instance_type == 'work_version' and work_version_id:
            success = core.assets.archive_work_version(work_version_id)
        return success

    # List commands

    def list_domains(self):
        domains = core.project.get_domains('name')
        return domains

    def list_categories(self, parent):
        # The parent argument should look like
        # "assets"
        categories = None
        instance_type, domain_id = core.assets.string_to_instance(parent)
        if domain_id:
            categories = core.project.get_domain_childs(domain_id, 'name')
        return categories

    def list_assets(self, parent):
        # The parent argument should look like
        # "assets/characters"
        assets = None
        instance_type, category_id = core.assets.string_to_instance(parent)
        if category_id:
            assets = core.project.get_category_childs(category_id, 'name')
        return assets

    def list_stages(self, parent):
        # The parent argument should look like
        # "assets/characters/Joe"
        stages = None
        instance_type, asset_id = core.assets.string_to_instance(parent)
        if asset_id:
            stages = core.project.get_asset_childs(asset_id, 'name')
        return stages

    def list_variants(self, parent):
        # The parent argument should look like
        # "assets/characters/Joe/modeling"
        variants = None
        instance_type, stage_id = core.assets.string_to_instance(parent)
        if stage_id:
            variants = core.project.get_stage_childs(stage_id, 'name')
        return variants

    def list_work_envs(self, parent):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main"
        work_envs = None
        instance_type, variant_id = core.assets.string_to_instance(parent)
        if variant_id:
            work_envs = core.project.get_variant_work_envs_childs(variant_id, 'name')
        return work_envs

    def list_work_versions(self, parent):
        # The parent argument should look like
        # "assets/characters/Joe/modeling/main/blender"
        work_versions = None
        instance_type, work_env_id = core.assets.string_to_work_instance(parent)
        if work_env_id:
            work_versions = core.project.get_work_versions(work_env_id, 'name')
        return work_versions

class tracking:
    def __init__(self):
        pass

    def get_task_assignment(self, variant):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            return core.project.get_variant_data(variant_id, 'assignment')

    def get_task_state(self, variant):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            return core.project.get_variant_data(variant_id, 'state')

    def get_task_work_time(self, variant):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            return core.project.get_variant_data(variant_id, 'work_time')

    def get_task_estimated_time(self, variant):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            return core.project.get_variant_data(variant_id, 'estimated_time')

    def assign_task(self, variant, user):
        user_id = core.site.get_user_row_by_name(user, 'id')
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if user_id and variant_id:
            core.assets.modify_variant_assignment(variant_id, user)

    def set_task_state(self, variant, state, comment=''):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            core.assets.modify_variant_state(variant_id, state, comment)

    def estimate_task_time(self, variant, time):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            core.assets.modify_variant_estimation(variant_id, time)    

    def add_task_comment(self, variant, comment):
        instance_type, variant_id = core.assets.string_to_instance(variant)
        if variant_id:
            core.assets.add_variant_comment(variant_id, comment)    

class launch:
    def __init__(self):
        pass

    def work_env(self, work_env):
        # Run the last version of the given work environment related software
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            last_work_version_id = core.project.get_last_work_version(work_env_id, 'id')
            if last_work_version_id:
                core.launch.launch_work_version(last_work_version_id[0])

    def work_version(self, work_version):
        # Run the given work version related software
        instance_type, work_version_id = core.assets.string_to_work_instance(work_version)
        if work_version_id:
            core.launch.launch_work_version(work_version_id)

    def kill_work_env(self, work_env):
        # Terminate the given work environment related software instance
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
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
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
        if work_env_id:
            core.project.set_work_env_lock(work_env_id, 1)

    def unlock_work_env(self, work_env):
        # Unlock the given work environment if it is locked by the current user
        instance_type, work_env_id = core.assets.string_to_work_instance(work_env)
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
        instance_type, instance_id = core.assets.string_to_instance(asset)
        if instance_type == 'asset':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_stage(self, stage):
        # Focus on the given stage in the project tree
        instance_type, instance_id = core.assets.string_to_instance(stage)
        if instance_type == 'stage':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_variant(self, variant):
        # Focus on the given variant in wizard
        instance_type, instance_id = core.assets.string_to_instance(variant)
        if instance_type == 'variant':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_work_version(self, work_version):
        # Focus on the given work version in the work versions tab
        instance_type, instance_id = core.assets.string_to_work_instance(work_version)
        if instance_type == 'work_version':
            gui.gui_server.focus_work_version(instance_id)

site = site()
user = user()
project = project()
assets = assets()
tracking = tracking()
launch = launch()
team = team()
ui = ui()
