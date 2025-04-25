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

"""
This module provides a set of classes and methods to interact with the Wizard framework.
It includes functionalities for managing repositories, users, projects, assets, tasks, 
launching environments, team collaboration, and user interfaces.

Classes:
- repository: Handles repository-related operations such as creating projects and users.
- user: Manages user-related operations like logging in, changing passwords, and preferences.
- project: Provides methods to manage project settings and software configurations.
- shelf: Allows creating and managing shelf tools and separators.
- assets: Handles asset creation, export, references, and archiving.
- tracking: Manages task assignments, states, and comments.
- launch: Provides methods to launch, kill, and manage work environments.
- team: Handles team collaboration and DNS settings.
- ui: Manages the user interface, including refreshing, focusing, and restarting.

Each class encapsulates specific functionalities, making it easier to interact with the Wizard framework.
"""

# Python modules
import logging

# Wizard modules
from wizard import core
from wizard import vars
from wizard import gui
logger = logging.getLogger(__name__)


class repository:
    """
    The `repository` class provides methods to interact with the core repository
    of the Wizard framework. It includes functionalities for managing projects,
    users, and repository-related operations.

    Methods:
        - projects(): Retrieves a list of project names.
        - create_project(): Creates a new project with specified parameters.
        - users(): Retrieves a list of user names from the repository.
        - flush_ips(): Clears or resets stored IP addresses in the repository.
        - create_user(): Creates a new user in the system.
        - upgrade_user_privilege(): Upgrades a user's privilege level to administrator.
        - downgrade_user_privilege(): Downgrades a user's privilege level.
    """

    def __init__(self):
        pass

    def projects(self):
        """
        Retrieves a list of project names.

        Returns:
            list: A list containing the names of all projects.
        """
        return core.repository.get_projects_names_list()

    def create_project(self, project_name,
                       project_path,
                       project_password,
                       frame_rate=24,
                       image_format=[1920, 1080]
                       ):
        """
        Creates a new project with the specified parameters.

        Args:
            project_name (str): The name of the project to be created.
            project_path (str): The file path where the project will be stored.
            project_password (str): The password to secure the project.
            frame_rate (int, optional): The frame rate for the project. Defaults to 24.
            image_format (list, optional): The resolution of the project in the format [width, height]. Defaults to [1920, 1080].

        Returns:
            object: The created project object.
        """
        return core.create_project.create_project(project_name,
                                                  project_path,
                                                  project_password,
                                                  frame_rate,
                                                  image_format
                                                  )

    def users(self):
        """
        Retrieves a list of user names from the repository.

        This method calls the `get_user_names_list` function from the 
        `core.repository` module to fetch the names of all users stored 
        in the repository.

        Returns:
            list: A list of user names.
        """
        return core.repository.get_user_names_list()

    def flush_ips(self):
        """
        Flushes the IPs stored in the core repository.

        This method calls the `flush_ips` function from the `core.repository` module
        to clear or reset the stored IP addresses.

        Returns:
            The result of the `core.repository.flush_ips()` call, which may vary
            depending on the implementation of the repository.
        """
        return core.repository.flush_ips()

    def create_user(self, user_name, user_password, email, administrator_pass=''):
        """
        Creates a new user in the system.

        Args:
            user_name (str): The username for the new user.
            user_password (str): The password for the new user.
            email (str): The email address of the new user.
            administrator_pass (str, optional): The administrator password required 
                for creating the user. Defaults to an empty string.

        Returns:
            Any: The result of the user creation process, as returned by the 
            core.repository.create_user method.
        """
        return core.repository.create_user(user_name,
                                           user_password,
                                           email,
                                           administrator_pass)

    def upgrade_user_privilege(self, user_name, administrator_pass):
        """
        Upgrades the privilege level of a specified user to administrator.

        Args:
            user_name (str): The username of the user whose privileges are to be upgraded.
            administrator_pass (str): The administrator password required to authorize the privilege upgrade.

        Returns:
            bool: True if the privilege upgrade is successful, False otherwise.
        """
        return core.repository.upgrade_user_privilege(user_name,
                                                      administrator_pass)

    def downgrade_user_privilege(self, user_name, administrator_pass):
        """
        Downgrades the privilege level of a specified user.

        This function interacts with the core repository to reduce the privilege
        level of a user. It requires the username of the target user and the 
        administrator's password for authentication.

        Args:
            user_name (str): The username of the user whose privileges are to be downgraded.
            administrator_pass (str): The password of the administrator authorizing the action.

        Returns:
            bool: True if the privilege downgrade was successful, False otherwise.
        """
        return core.repository.downgrade_user_privilege(user_name,
                                                        administrator_pass)


class user:
    def __init__(self):
        pass

    def set(self, user_name, password):
        """
        Authenticates a user by their username and password, and restarts the GUI server if authentication is successful.

        Args:
            user_name (str): The username of the user attempting to log in.
            password (str): The password of the user attempting to log in.

        Returns:
            None
        """
        if core.user.log_user(user_name, password):
            gui.gui_server.restart_ui()

    def get(self):
        """
        Retrieves the current user's information from the environment.

        Returns:
            dict: A dictionary containing details about the current user.
        """
        return core.environment.get_user()

    def change_password(self, old_password, new_password):
        """
        Changes the password for the currently authenticated user.

        Args:
            old_password (str): The current password of the user.
            new_password (str): The new password to set for the user.

        Returns:
            bool: True if the password was successfully changed, False otherwise.

        Raises:
            ValueError: If the old password is incorrect or the new password does not meet security requirements.
        """
        return core.repository.modify_user_password(core.environment.get_user(),
                                                    old_password,
                                                    new_password)

    def is_admin(self):
        """
        Checks if the current user has administrative privileges.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return core.repository.is_admin()

    def set_team_dns(self, host, port):
        """
        Sets the team server DNS as a user preference.

        Args:
            host (str): The hostname or IP address of the team server.
            port (int): The port number of the team server.

        Returns:
            bool: True if the DNS was successfully set, False otherwise.
        """
        return core.user.user().set_team_dns(host, port)

    def get_team_dns(self):
        """
        Retrieves the DNS (Domain Name System) information for the team.

        Returns:
            str: The DNS information associated with the team.
        """
        return core.environment.get_team_dns()

    def set_popups_settings(self, enabled=1, duration=3, keep_until_comment=True):
        """
        Configures the settings for popups.

        Args:
            enabled (int, optional): Determines whether popups are enabled. 
                Defaults to 1 (enabled). Use 0 to disable.
            duration (int, optional): The duration (in seconds) for which the popup 
                should be displayed. Defaults to 3 seconds.
            keep_until_comment (bool, optional): If True, the popup will remain 
                visible until a comment is made. Defaults to True.

        Returns:
            Any: The result of the `set_popups_settings` method from the core user object.
        """
        return core.user.user().set_popups_settings(enabled, duration, keep_until_comment)


class project:
    """
    The `project` class provides methods to manage and interact with a project in the system.
    This class includes functionalities such as logging into a project, retrieving project details,
    changing the project password, and configuring software executables associated with the project.
    Methods:
        __init__:
            Initializes the `project` class.
        set(project_name, project_password):
            Logs into a project using the provided name and password, and restarts the GUI server if successful.
        name():
            Retrieves the name of the current project from the environment configuration.
        path():
            Retrieves the file path of the current project from the environment configuration.
        change_password(old_password, new_password, administrator_pass):
            Changes the password for the current project with administrator authorization.
        set_software_executable(software_name, executable_path):
            Sets the executable path for a specified software in the project configuration.
        set_software_batch_executable(software_name, batch_executable_path):
            Sets the batch executable path for a specified software in the project configuration.
    """

    def __init__(self):
        pass

    def set(self, project_name, project_password):
        """
        Sets the project by logging in with the provided project name and password.
        If the login is successful, the GUI server is restarted.

        Args:
            project_name (str): The name of the project to log in to.
            project_password (str): The password for the project.

        Returns:
            None
        """
        if core.user.log_project(project_name, project_password):
            gui.gui_server.restart_ui()

    def name(self):
        """
        Retrieves the name of the current project.

        Returns:
            str: The name of the project as obtained from the environment configuration.
        """
        return core.environment.get_project_name()

    def path(self):
        """
        Retrieve the project path from the core environment.

        Returns:
            str: The project path as defined in the core environment.
        """
        return core.environment.get_project_path()

    def change_password(self, old_password, new_password, administrator_pass):
        """
        Changes the password for the current project.

        Args:
            old_password (str): The current password of the project.
            new_password (str): The new password to set for the project.
            administrator_pass (str): The administrator's password for authorization.

        Returns:
            bool: True if the password was successfully changed, False otherwise.
        """
        return core.repository.modify_project_password(core.environment.get_project_name(),
                                                       old_password,
                                                       new_password,
                                                       administrator_pass)

    def set_software_executable(self, software_name, executable_path):
        """
        Sets the executable path for a specified software.

        Args:
            software_name (str): The name of the software for which the executable path is being set.
            executable_path (str): The file path to the software's executable.

        Returns:
            None
        """
        software_id = core.project.get_software_data_by_name(
            software_name, 'id')
        if software_id:
            core.project.set_software_path(software_id, executable_path)

    def set_software_batch_executable(self, software_name, batch_executable_path):
        """
        Sets the batch executable path for a specified software.

        This function retrieves the software ID based on the provided software name
        and updates its batch executable path in the project configuration.

        Args:
            software_name (str): The name of the software for which the batch executable path is to be set.
            batch_executable_path (str): The file path to the batch executable for the specified software.

        Returns:
            None
        """
        software_id = core.project.get_software_data_by_name(
            software_name, 'id')
        if software_id:
            core.project.set_software_batch_path(
                software_id, batch_executable_path)


class shelf:
    """
    A class to manage and create shelf tools and separators.
    Methods:
        __init__():
            Initializes the shelf class.
        create_shelf_tool(name, script, help, only_subprocess=0, icon=vars.ressources._default_script_shelf_icon_):
            Creates a shelf tool with the specified parameters.
            Args:
                name (str): The name of the shelf tool.
                script (str): The script or command associated with the shelf tool.
                help (str): A description or help text for the shelf tool.
                only_subprocess (int, optional): Indicates if the tool should only run in a subprocess. Defaults to 0.
                icon (str, optional): The icon to represent the shelf tool. Defaults to vars.ressources._default_script_shelf_icon_.
            Returns:
                object: The created shelf tool.
        create_separator():
            Creates a separator for the shelf.
            Returns:
                object: The created shelf separator.
    """

    def __init__(self):
        pass

    def create_shelf_tool(self, name, script, help, only_subprocess=0, icon=vars.ressources._default_script_shelf_icon_):
        """
        Creates a shelf tool in the project with the specified parameters.

        Args:
            name (str): The name of the shelf tool.
            script (str): The script or command to be executed by the shelf tool.
            help (str): A description or help text for the shelf tool.
            only_subprocess (int, optional): If set to 1, the tool will only run in a subprocess. Defaults to 0.
            icon (str, optional): The path to the icon for the shelf tool. Defaults to `vars.ressources._default_script_shelf_icon_`.

        Returns:
            object: The created shelf tool object.
        """
        return core.shelf.create_project_script(name, script, help, only_subprocess, icon)

    def create_separator(self):
        """
        Creates a separator in the shelf.

        This method utilizes the `create_separator` function from the `core.shelf` module
        to add a visual separator element.

        Returns:
            The result of the `core.shelf.create_separator()` function, which typically
            represents the created separator object or a success indicator.
        """
        return core.shelf.create_separator()


class assets:
    def __init__(self):
        pass

    # Creation commands

    def create_sequence(self, name):
        """
        Creates a new sequence category with the given name and returns its string representation.

        Args:
            name (str): The name of the sequence to be created.

        Returns:
            str or None: The string representation of the created sequence category if successful,
                 otherwise None.
        """
        string_sequence = None
        sequence_id = core.assets.create_category(name, 3)
        if sequence_id:
            string_sequence = core.assets.instance_to_string(('category',
                                                              sequence_id))
        return string_sequence

    def create_asset(self, parent, name):
        """
        Creates an asset under a specified parent category.
        Args:
            parent (str or int): The parent category for the asset. If a string, it should
                represent the category path (e.g., "assets/characters"). If an integer, it
                should represent the category ID directly.
            name (str): The name of the asset to be created.
        Returns:
            str or None: A string representation of the created asset if successful,
            otherwise None.
        """
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
        """
        Creates a new stage associated with a given parent asset.
        Args:
            parent (str or int): The parent asset identifier. If a string is provided, 
                it will be converted to an asset ID. If an integer is provided, it is 
                assumed to be the asset ID directly.
            stage (str): The name or identifier of the stage to be created.
        Returns:
            str or None: A string representation of the created stage if successful, 
                otherwise None.
        """
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
        """
        Creates a variant associated with a given parent and returns its string representation.
        Args:
            parent (str or int): The parent identifier. If a string is provided, it is converted 
                     to an instance type and stage ID. If an integer is provided, it 
                     is treated as the stage ID directly.
            name (str): The name of the variant to be created.
        Returns:
            str or None: The string representation of the created variant if successful, 
                 otherwise None.
        """
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
        """
        Creates a work environment for a given parent and software.
        Args:
            parent (str or int): The parent identifier, which can either be a string 
                representing an instance or an integer representing a variant ID.
            software (str): The name of the software for which the work environment 
                is being created.
        Returns:
            str or None: A string representation of the created work environment 
                if successful, otherwise None.
        Notes:
            - If `parent` is a string, it is converted to an instance type and 
              variant ID using `core.assets.string_to_instance`.
            - The function retrieves the software ID using the software name and 
              creates a work environment associated with the given variant ID.
            - If the work environment is successfully created, it is converted 
              back to a string representation using `core.assets.instance_to_string`.
        """
        string_work_env = None

        if type(parent) == str:
            instance_type, variant_id = core.assets.string_to_instance(parent)
        else:
            variant_id = parent

        if variant_id:
            software_id = core.assets.get_software_id_by_name(software)
            if software_id:
                work_env_id = core.assets.create_work_env(
                    software_id, variant_id)
                if work_env_id:
                    string_work_env = core.assets.instance_to_string(('work_env',
                                                                      work_env_id))
        return string_work_env

    # Exports commands

    def create_export(self, variant, export_name, files_list, comment=''):
        """
        Creates an export version for a given variant.
        Args:
            variant (str or int): The variant identifier. If a string is provided, 
                it will be converted to an instance type and variant ID. If an integer 
                is provided, it is assumed to be the variant ID.
            export_name (str): The name of the export to be created.
            files_list (list): A list of file paths to be included in the export.
            comment (str, optional): An optional comment or description for the export. 
                Defaults to an empty string.
        Returns:
            bool or None: Returns True if the export is successfully created, False if 
                the operation fails, or None if the variant ID is invalid or the instance 
                type is not 'variant'.
        """
        success = None

        if type(variant) == str:
            instance_type, variant_id = core.assets.string_to_instance(variant)
        else:
            variant_id = variant

        if variant_id and instance_type == 'variant':
            success = core.assets.merge_file_as_export_version(
                export_name, files_list, variant_id, comment)
        return success

    def batch_export(self, work_env, namespaces_list=[], rolls=False, custom_frame_range=None, refresh_assets_in_scene=False):
        """
        Exports a batch of assets based on the provided work environment and settings.
        Args:
            work_env (str or int): The work environment identifier. Can be a string 
                representing the work environment or an integer ID.
            namespaces_list (list, optional): A list of namespaces to include in the export. 
                Defaults to an empty list.
            rolls (bool, optional): If True, includes preroll and postroll frames in the 
                export frame range. Defaults to False.
            custom_frame_range (list, optional): A custom frame range to override the 
                default in/out frames. Should be a list of two integers [start_frame, end_frame]. 
                Defaults to None.
            refresh_assets_in_scene (bool, optional): If True, refreshes assets in the 
                scene before exporting. Defaults to False.
        Raises:
            ValueError: If the provided work environment is invalid or the version ID 
                cannot be determined.
        Notes:
            - The function determines the frame range based on the asset's inframe and 
              outframe unless a custom frame range is provided.
            - If `rolls` is True, the preroll and postroll values are added to the frame range.
            - The export process is handled by the `core.subtasks_library.batch_export` method.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id and instance_type == 'work_env':
            version_id = core.project.get_last_work_version(work_env_id, 'id')
            if version_id:
                version_id = version_id[0]
                stage = core.assets.get_stage_data_from_work_env_id(
                    work_env_id, 'name')
                asset_row = core.assets.get_asset_data_from_work_env_id(
                    work_env_id)
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
        """
        Exports camera data in batch mode for a given work environment.
        Args:
            work_env (str or int): The work environment identifier. Can be a string 
                representing the work environment or an integer ID.
            namespaces_list (list, optional): A list of namespaces to include in the export. 
                Defaults to an empty list.
            rolls (bool, optional): If True, includes preroll and postroll frames in the 
                frame range. Defaults to False.
            custom_frame_range (list, optional): A custom frame range to use for the export. 
                If not provided, the frame range is determined from the asset data. 
                Defaults to None.
            refresh_assets_in_scene (bool, optional): If True, refreshes assets in the scene 
                before exporting. Defaults to False.
        Raises:
            ValueError: If the provided work environment is invalid or does not exist.
        Notes:
            - The function determines the frame range based on the asset's inframe and 
              outframe unless a custom frame range is provided.
            - If `rolls` is True, the preroll and postroll values are added to the frame range.
            - The export settings are passed to the `core.subtasks_library.batch_export` 
              function for processing.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id and instance_type == 'work_env':
            version_id = core.project.get_last_work_version(work_env_id, 'id')
            if version_id:
                version_id = version_id[0]
                # stage = core.assets.get_stage_data_from_work_env_id(work_env_id, 'name')
                asset_row = core.assets.get_asset_data_from_work_env_id(
                    work_env_id)
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
        """
        Creates a new group with the specified name.

        Args:
            name (str): The name of the group to be created.

        Returns:
            Group: The created group object.

        """
        return core.assets.create_group(name)

    def modify_group_color(self, group, color):
        """
        Modifies the color of a specified group.
        Args:
            group (str or int): The group identifier. Can be a string representing 
                    the group name or an integer representing the group ID.
            color: The new color to assign to the group. The type and format of this 
               parameter depend on the implementation of `core.project.modify_group_color`.
        Returns:
            bool or None: Returns True if the color modification is successful, 
                  False if it fails, or None if the group is not found.
        """
        success = None

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            success = core.project.modify_group_color(group_id, color)
        return success

    def delete_group(self, group):
        """
        Deletes a group by its name or ID.
        Args:
            group (str or int): The group to delete. Can be a string representing
                the group name or an integer representing the group ID.
        Returns:
            bool or None: Returns True if the group was successfully deleted,
                False if the deletion failed, or None if the group was not found.
        """
        success = None

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            success = core.assets.remove_group(group_id)
        return success

    # References commands

    def create_reference(self, destination_work_env, stage_to_reference):
        """
        Creates a reference to a specified stage in a given work environment.
        This function establishes a reference between a destination work environment
        and a stage to be referenced. It supports both string and object representations
        of the work environment and stage.
        Args:
            destination_work_env (str or object): The destination work environment, 
                either as a string identifier or an object.
            stage_to_reference (str or object): The stage to reference, either as a 
                string identifier or an object.
        Returns:
            list: A list of new references created in the destination work environment, 
            or None if the operation fails.
        Notes:
            - The function uses `core.assets.string_to_work_instance` and 
              `core.assets.string_to_instance` to convert string representations to 
              their respective object types.
            - References are created using `core.assets.create_references_from_stage_id`.
            - The difference between the old and new references is calculated to 
              determine the newly added references.
        """
        new_references = None

        if type(destination_work_env) == str:
            dest_instance_type, work_env_id = core.assets.string_to_work_instance(
                destination_work_env)
        else:
            work_env_id = destination_work_env

        if type(stage_to_reference) == str:
            orig_instance_type, stage_id = core.assets.string_to_instance(
                stage_to_reference)
        else:
            stage_id = stage_to_reference

        if work_env_id and stage_id:
            old_references = core.project.get_references(
                work_env_id, 'namespace')
            core.assets.create_references_from_stage_id(work_env_id, stage_id)
            new_references = list(set(core.project.get_references(
                work_env_id, 'namespace')) - set(old_references))
        return new_references

    def create_grouped_reference(self, destination_group, stage_to_reference):
        """
        Creates grouped references for a given destination group and stage.
        This function generates new references by associating a stage with a 
        destination group. It supports both string and non-string inputs for 
        the destination group and stage to reference.
        Args:
            destination_group (str or int): The destination group, either as a 
                string (group name) or an integer (group ID).
            stage_to_reference (str or int): The stage to reference, either as a 
                string (stage name) or an integer (stage ID).
        Returns:
            list: A list of newly created grouped references (namespaces), or 
            None if the operation fails.
        Notes:
            - If `destination_group` is a string, it is converted to a group ID.
            - If `stage_to_reference` is a string, it is converted to a stage ID.
            - The function calculates the difference between the old and new 
              grouped references to determine the newly created references.
        """
        new_references = None

        if type(destination_group) == str:
            group_id = core.project.get_group_by_name(destination_group, 'id')
        else:
            group_id = destination_group

        if type(stage_to_reference) == str:
            orig_instance_type, stage_id = core.assets.string_to_instance(
                stage_to_reference)
        else:
            stage_id = stage_to_reference

        if group_id and stage_id:
            old_references = core.project.get_grouped_references(
                group_id, 'namespace')
            core.assets.create_grouped_references_from_stage_id(
                group_id, stage_id)
            new_references = list(set(core.project.get_grouped_references(
                group_id, 'namespace')) - set(old_references))
        return new_references

    def create_referenced_group(self, destination_work_env, group):
        """
        Creates a referenced group in the specified destination work environment.
        Args:
            destination_work_env (str or int): The destination work environment, 
                either as a string (to be converted to a work instance) or as an integer ID.
            group (str or int): The group to be referenced, either as a string 
                (to be resolved to a group ID) or as an integer ID.
        Raises:
            ValueError: If the destination work environment or group cannot be resolved.
        """
        if type(destination_work_env) == str:
            dest_instance_type, work_env_id = core.assets.string_to_work_instance(
                destination_work_env)
        else:
            work_env_id = destination_work_env

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if work_env_id and group_id:
            core.assets.create_referenced_group(work_env_id, group_id)

    def get_references(self, work_env):
        """
        Retrieve references associated with a given work environment.
        Args:
            work_env (str or int): The work environment identifier. If a string is 
                provided, it will be converted to a work instance ID. If an integer 
                is provided, it is assumed to be the work environment ID.
        Returns:
            list or None: A list of references associated with the work environment 
                in 'namespace' format, or None if the work environment ID is invalid.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            return core.project.get_references(work_env_id, 'namespace')
        else:
            return None

    def get_references_from_group(self, group):
        """
        Retrieves references associated with a specified group.
        Args:
            group (str or int): The group identifier. If a string is provided, it is
                treated as the group name and converted to its corresponding ID. If an
                integer is provided, it is treated as the group ID directly.
        Returns:
            list or None: A list of references associated with the group, organized by
                namespace, if the group exists. Returns None if the group does not exist.
        """
        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            return core.project.get_grouped_references(group_id, 'namespace')
        else:
            return None

    def get_referenced_groups(self, work_env):
        """
        Retrieves the referenced groups associated with a given work environment.
        Args:
            work_env (str or int): The work environment identifier. It can be a string
                representing the work environment or an integer ID.
        Returns:
            list or None: A list of referenced groups in the 'namespace' of the given
                work environment if the ID is valid. Returns None if the work environment
                ID is invalid or not provided.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            return core.project.get_referenced_groups(work_env_id, 'namespace')
        else:
            return None

    def remove_reference(self, work_env, reference):
        """
        Removes a reference from a specified work environment.
        Args:
            work_env (str or int): The work environment from which the reference 
                should be removed. It can be a string representing the work 
                environment or an integer ID.
            reference (str): The namespace or identifier of the reference to be removed.
        Returns:
            bool: True if the reference was successfully removed, False otherwise.
        Notes:
            - If `work_env` is provided as a string, it will be converted to a 
              work environment ID using `core.assets.string_to_work_instance`.
            - The function retrieves the reference ID using 
              `core.project.get_reference_by_namespace` and removes it using 
              `core.assets.remove_reference`.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(
                work_env_id, reference, 'id')
            if reference_id:
                return core.assets.remove_reference(reference_id)

    def remove_reference_from_group(self, group, reference):
        """
        Removes a reference from a specified group.
        Args:
            group (str or int): The group from which the reference should be removed. 
                If a string is provided, it is treated as the group name, and the group ID 
                is retrieved. If an integer is provided, it is treated as the group ID.
            reference (str): The reference to be removed from the group.
        Returns:
            bool: True if the reference was successfully removed, False otherwise.
        Notes:
            - If the group is provided as a name (string), the function retrieves the 
              corresponding group ID using `core.project.get_group_by_name`.
            - If the group ID is valid, the function retrieves the grouped reference ID 
              using `core.project.get_grouped_reference_by_namespace`.
            - If the grouped reference ID is found, the function removes the grouped 
              reference using `core.assets.remove_grouped_reference`.
        """
        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(
                group_id, reference, 'id')
            if grouped_reference_id:
                return core.assets.remove_grouped_reference(grouped_reference_id)

    def remove_referenced_group(self, work_env, referenced_group):
        """
        Removes a referenced group from a specified work environment.
        Args:
            work_env (str or int): The work environment identifier. Can be a string
                representing the work environment or an integer ID.
            referenced_group (str): The name of the referenced group to be removed.
        Returns:
            bool: True if the referenced group was successfully removed, False otherwise.
        Notes:
            - If `work_env` is provided as a string, it will be converted to a work
              environment ID using `core.assets.string_to_work_instance`.
            - The function retrieves the ID of the referenced group using
              `core.project.get_referenced_group_by_namespace` before attempting to
              remove it.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            referenced_group_id = core.project.get_referenced_group_by_namespace(
                work_env_id, referenced_group, 'id')
            if referenced_group_id:
                return core.assets.remove_referenced_group(referenced_group_id)

    def set_reference_as_default(self, work_env, reference):
        """
        Sets the specified reference as the default version in the given work environment.
        Args:
            work_env (str or int): The work environment, which can be provided as a string 
            (to be converted to a work instance) or directly as an ID.
            reference (str): The namespace of the reference to be set as default.
        Returns:
            bool: True if the reference was successfully set to its last version, 
            False otherwise.
        Notes:
            - If `work_env` is a string, it will be converted to a work instance ID.
            - The function retrieves the reference ID by its namespace and sets it to 
              its latest version if found.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(
                work_env_id, reference, 'id')
            if reference_id:
                return core.assets.set_reference_last_version(reference_id)

    def set_grouped_reference_as_default(self, group, reference):
        """
        Sets the specified grouped reference as the default by marking it as the last version.
        Args:
            group (str or int): The group identifier. If a string is provided, it is treated as 
                the group name and resolved to its ID. If an integer is provided, it is treated 
                as the group ID directly.
            reference (str): The namespace of the grouped reference to be set as default.
        Returns:
            bool: True if the grouped reference was successfully set as the last version, 
                False otherwise.
        """
        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(
                group_id, reference, 'id')
            if grouped_reference_id:
                return core.assets.set_grouped_reference_last_version(grouped_reference_id)

    def modify_reference_auto_update(self, work_env, reference, auto_update=True):
        """
        Modifies the auto-update setting for a reference in a given work environment.
        Args:
            work_env (str or int): The work environment, either as a string (to be 
                converted to an instance type and ID) or directly as an ID.
            reference (str): The namespace of the reference to modify.
            auto_update (bool, optional): Whether to enable (True) or disable (False) 
                auto-update for the reference. Defaults to True.
        Returns:
            bool: True if the modification was successful, False otherwise.
        """
        if auto_update:
            auto_update = 1
        else:
            auto_update = 0

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            reference_id = core.project.get_reference_by_namespace(
                work_env_id, reference, 'id')
            if reference_id:
                return core.project.modify_reference_auto_update(reference_id, auto_update)

    def modify_grouped_reference_auto_update(self, group, reference, auto_update=True):
        """
        Modifies the auto-update setting for a grouped reference in a project.
        Args:
            group (str or int): The group identifier, which can be either the group name (str) 
                or the group ID (int).
            reference (str): The namespace or identifier of the reference to be modified.
            auto_update (bool, optional): A flag indicating whether auto-update should be enabled (True) 
                or disabled (False). Defaults to True.
        Returns:
            bool: True if the modification was successful, False otherwise.
        Notes:
            - If `group` is provided as a string, it will be resolved to its corresponding group ID.
            - If the group or grouped reference cannot be found, the function will return False.
        """
        if auto_update:
            auto_update = 1
        else:
            auto_update = 0

        if type(group) == str:
            group_id = core.project.get_group_by_name(group, 'id')
        else:
            group_id = group

        if group_id:
            grouped_reference_id = core.project.get_grouped_reference_by_namespace(
                group_id, reference, 'id')
            if grouped_reference_id:
                return core.project.modify_grouped_reference_auto_update(grouped_reference_id, auto_update)

    # Archive commands

    def archive_asset(self, asset):
        """
        Archives the specified asset.
        Args:
            asset (str or int): The asset to be archived. If a string is provided, 
                it will be parsed to extract the instance type and asset ID. If an 
                integer is provided, it is assumed to be the asset ID.
        Returns:
            bool or None: Returns True if the asset was successfully archived, 
                False if the operation failed, or None if the asset ID could not 
                be determined.
        """
        success = None

        if type(asset) == str:
            instance_type, asset_id = core.assets.string_to_instance(asset)
        else:
            asset_id = asset

        if asset_id:
            success = core.assets.archive_asset(asset_id)
        return success

    def archive_sequence(self, sequence):
        """
        Archives a sequence based on the provided sequence identifier or string.
        Args:
            sequence (str or int): The sequence to archive. It can be either:
                - A string representing the sequence, which will be converted to an instance type and sequence ID.
                - An integer representing the sequence ID directly.
        Returns:
            bool or None: Returns True if the sequence was successfully archived, 
                          False if the archiving failed, or None if the sequence ID is invalid.
        """
        success = None

        if type(sequence) == str:
            instance_type, sequence_id = core.assets.string_to_instance(
                sequence)
        else:
            sequence_id = sequence

        if sequence_id:
            success = core.assets.archive_category(sequence_id)
        return success

    def archive_stage(self, stage):
        """
        Archives a specified stage by its identifier or string representation.
        Args:
            stage (Union[str, int]): The stage to archive. Can be provided as a string
                representation or as an integer ID.
        Returns:
            bool: True if the stage was successfully archived, False otherwise.
                  Returns None if the stage ID is invalid or the operation fails.
        Notes:
            - If the input is a string, it will be converted to an instance type and stage ID
              using `core.assets.string_to_instance`.
            - The actual archiving operation is performed by `core.assets.archive_stage`.
        """
        success = None

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            success = core.assets.archive_stage(stage_id)
        return success

    def archive_variant(self, variant):
        """
        Archives a variant based on the provided identifier.
        Args:
            variant (str or int): The variant to archive. If a string is provided, 
                it will be parsed to extract the instance type and variant ID. 
                If an integer is provided, it is assumed to be the variant ID.
        Returns:
            bool or None: Returns True if the variant was successfully archived, 
                False if the operation failed, or None if the variant ID could not 
                be determined.
        """
        success = None

        if type(variant) == str:
            instance_type, variant_id = core.assets.string_to_instance(variant)
        else:
            variant_id = variant

        if variant_id:
            success = core.assets.archive_variant(variant_id)
        return success

    def archive_work_env(self, work_env):
        """
        Archives a work environment based on the provided identifier.
        Args:
            work_env (str or int): The work environment to archive. If a string is 
                provided, it is assumed to be a serialized representation of the 
                work environment, which will be parsed to extract the instance type 
                and ID. If an integer is provided, it is treated as the work 
                environment ID directly.
        Returns:
            bool or None: Returns True if the work environment was successfully 
                archived, False if the operation failed, or None if the input was 
                invalid or the operation could not be performed.
        """
        success = None

        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            instance_type = 'work_env'
            work_env_id = work_env

        if instance_type == 'work_env' and work_env_id:
            success = core.assets.archive_work_env(work_env_id)
        return success

    def archive_work_version(self, work_version):
        """
        Archives a work version based on the provided identifier.
        Args:
            work_version (str or int): The identifier of the work version to archive.
                - If a string, it will be parsed to extract the instance type and ID.
                - If an integer, it is assumed to be the work version ID.
        Returns:
            bool or None: 
                - True if the work version was successfully archived.
                - False if the archiving process failed.
                - None if the input is invalid or the operation could not be performed.
        """
        success = None

        if type(work_version) == str:
            instance_type, work_version_id = core.assets.string_to_work_instance(
                work_version)
        else:
            instance_type = 'work_version'
            work_version_id = work_version

        if instance_type == 'work_version' and work_version_id:
            success = core.assets.archive_work_version(work_version_id)
        return success

    # List commands

    def list_domains(self, column='*'):
        """
        Retrieves a list of domains from the project.

        Args:
            column (str): The specific column to retrieve from the domains. 
                          Defaults to '*' which retrieves all columns.

        Returns:
            list: A list of domains retrieved from the project.
        """
        domains = core.project.get_domains(column)
        return domains

    def list_categories(self, parent, column='*'):
        """
        Retrieves a list of categories based on the given parent identifier.
        Args:
            parent (str or int): The parent identifier, which can be a string 
                representing an instance or an integer representing a domain ID.
            column (str, optional): The column(s) to retrieve from the database. 
                Defaults to '*', which selects all columns.
        Returns:
            list or None: A list of categories if the domain ID is valid, 
                otherwise None.
        """
        categories = None

        if type(parent) == str:
            instance_type, domain_id = core.assets.string_to_instance(parent)
        else:
            domain_id = parent

        if domain_id:
            categories = core.project.get_domain_childs(domain_id, column)
        return categories

    def list_assets(self, parent, column='*'):
        """
        Retrieves a list of assets based on the given parent identifier.
        Args:
            parent (str or int): The parent identifier, which can be a string 
                representing an instance or a category ID.
            column (str, optional): The column(s) to retrieve from the assets. 
                Defaults to '*', which retrieves all columns.
        Returns:
            list or None: A list of assets if the category ID is valid, 
                otherwise None.
        """
        assets = None

        if type(parent) == str:
            instance_type, category_id = core.assets.string_to_instance(parent)
        else:
            category_id = parent

        if category_id:
            assets = core.project.get_category_childs(category_id, column)
        return assets

    def list_stages(self, parent, column='*'):
        """
        Retrieves the stages (child assets) of a given parent asset.
        Args:
            parent (str or int): The parent asset identifier. If a string is provided, 
                it will be converted to an asset ID. If an integer is provided, it is 
                assumed to be the asset ID directly.
            column (str, optional): The column(s) to retrieve for the child assets. 
                Defaults to '*', which retrieves all columns.
        Returns:
            list or None: A list of child assets (stages) if the parent asset ID is valid, 
                otherwise None.
        """
        stages = None

        if type(parent) == str:
            instance_type, asset_id = core.assets.string_to_instance(parent)
        else:
            asset_id = parent

        if asset_id:
            stages = core.project.get_asset_childs(asset_id, column)
        return stages

    def list_variants(self, parent, column='*'):
        """
        Retrieves a list of variants associated with a given parent identifier.
        Args:
            parent (str or int): The parent identifier, which can be a string 
                representing an instance or an integer representing a stage ID.
            column (str, optional): The column(s) to retrieve from the database. 
                Defaults to '*', which selects all columns.
        Returns:
            list or None: A list of variants if the stage ID is valid, otherwise None.
        """
        variants = None

        if type(parent) == str:
            instance_type, stage_id = core.assets.string_to_instance(parent)
        else:
            stage_id = parent

        if stage_id:
            variants = core.project.get_stage_childs(stage_id, column)
        return variants

    def list_work_envs(self, parent, column='*'):
        """
        Retrieves a list of work environments associated with a given parent.
        Args:
            parent (str or int): The parent identifier. If a string is provided, it is 
                converted to an instance type and variant ID. If an integer is provided, 
                it is treated as the variant ID directly.
            column (str, optional): The column(s) to retrieve from the work environments. 
                Defaults to '*' (all columns).
        Returns:
            list or None: A list of work environments if the variant ID is valid, 
            otherwise None.
        """
        work_envs = None

        if type(parent) == str:
            instance_type, variant_id = core.assets.string_to_instance(parent)
        else:
            variant_id = parent

        if variant_id:
            work_envs = core.project.get_variant_work_envs_childs(
                variant_id, column)
        return work_envs

    def list_work_versions(self, parent, column='*'):
        """
        Retrieves a list of work versions associated with a given parent identifier.
        Args:
            parent (str or int): The parent identifier, which can be either a string 
                representing a work instance or an integer representing a work environment ID.
            column (str, optional): The column(s) to retrieve from the work versions. 
                Defaults to '*', which retrieves all columns.
        Returns:
            list or None: A list of work versions if the work environment ID is valid, 
                otherwise None.
        """
        work_versions = None

        if type(parent) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                parent)
        else:
            work_env_id = parent

        if work_env_id:
            work_versions = core.project.get_work_versions(work_env_id, column)
        return work_versions

    def list_exports(self, parent, column='*'):
        """
        Retrieves a list of exports associated with a given parent stage.
        Args:
            parent (str or int): The parent identifier, which can be a string 
                representing an instance or an integer representing a stage ID.
            column (str, optional): The column(s) to retrieve from the exports. 
                Defaults to '*' (all columns).
        Returns:
            list or None: A list of exports if the stage ID is valid, otherwise None.
        """
        exports = None

        if type(parent) == str:
            instance_type, stage_id = core.assets.string_to_instance(parent)
        else:
            stage_id = parent

        if stage_id:
            exports = core.project.get_stage_export_childs(stage_id, column)
        return exports

    def list_export_versions(self, parent, column='*'):
        """
        Retrieves a list of export versions for a given parent export ID or string representation.
        Args:
            parent (str or int): The parent export identifier. It can be a string 
                representation of the export instance or an integer export ID.
            column (str, optional): The column(s) to retrieve from the export versions. 
                Defaults to '*' (all columns).
        Returns:
            list or None: A list of export versions if the export ID is valid, 
                otherwise None.
        """
        export_versions = None

        if type(parent) == str:
            instance_type, export_id = core.assets.string_to_export_instance(
                parent)
        else:
            export_id = parent

        if export_id:
            export_versions = core.project.get_export_childs(export_id, column)
        return export_versions


class tracking:
    """
    A class to manage task tracking operations, including retrieving task details, 
    assigning tasks, updating task states, estimating task times, and adding comments.
    Methods
    -------
    get_task_assignment(stage):
        Retrieves the assignment information for a given task stage.
    get_task_state(stage):
        Retrieves the current state of a given task stage.
    get_task_work_time(stage):
        Retrieves the work time logged for a given task stage.
    get_task_estimated_time(stage):
        Retrieves the estimated time for a given task stage.
    assign_task(stage, user):
        Assigns a task stage to a specified user.
    set_task_state(stage, state, comment=''):
        Updates the state of a task stage with an optional comment.
    estimate_task_time(stage, time):
        Sets the estimated time for a given task stage.
    add_task_comment(stage, comment):
        Adds a comment to a given task stage.
    """

    def __init__(self):
        pass

    def get_task_assignment(self, stage):
        """
        Retrieve the task assignment for a given stage.
        Args:
            stage (str or int): The stage identifier. If a string is provided, it will
                be converted to an instance type and stage ID. If an integer is provided,
                it is treated as the stage ID directly.
        Returns:
            dict or None: The assignment data for the specified stage if the stage ID
            is valid, otherwise None.
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'assignment')

    def get_task_state(self, stage):
        """
        Retrieve the state of a specific task stage.
        Args:
            stage (str or int): The stage identifier. If a string is provided, it will
                be converted to an instance type and stage ID. If an integer is provided,
                it is treated as the stage ID directly.
        Returns:
            str or None: The state of the specified stage if the stage ID is valid,
            otherwise None.
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'state')

    def get_task_work_time(self, stage):
        """
        Retrieve the work time associated with a specific task stage.
        Args:
            stage (str or int): The stage identifier, which can be either a string
                representation of the stage or an integer stage ID.
        Returns:
            float or None: The work time for the specified stage if it exists,
                otherwise None.
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'work_time')

    def get_task_estimated_time(self, stage):
        """
        Retrieve the estimated time for a specific task stage.
        Args:
            stage (str or int): The stage identifier. It can be a string representing
                the stage in a specific format or an integer representing the stage ID.
        Returns:
            float or None: The estimated time for the given stage in hours, or None
            if the stage ID is invalid or the data is unavailable.
        Raises:
            ValueError: If the input stage string cannot be converted to a valid instance.
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            return core.project.get_stage_data(stage_id, 'estimated_time')

    def assign_task(self, stage, user):
        """
        Assigns a task to a user for a specific stage.
        Args:
            stage (str or int): The stage to assign the task to. If a string is provided, 
                                it will be converted to an instance type and stage ID.
            user (str): The name of the user to whom the task will be assigned.
        Returns:
            None
        Notes:
            - The function retrieves the user ID based on the provided username.
            - If the stage is provided as a string, it is converted to a stage ID.
            - The task assignment is modified only if both the user ID and stage ID are valid.
        """
        user_id = core.repository.get_user_row_by_name(user, 'id')

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if user_id and stage_id:
            core.assets.modify_stage_assignment(stage_id, user)

    def set_task_state(self, stage, state, comment=''):
        """
        Updates the state of a specified task stage.
        Args:
            stage (str or int): The stage identifier. If a string is provided, it will
                be converted to an instance type and stage ID. If an integer is provided,
                it is treated as the stage ID directly.
            state (str): The new state to set for the task stage.
            comment (str, optional): An optional comment to associate with the state change.
                Defaults to an empty string.
        Raises:
            ValueError: If the stage cannot be resolved to a valid stage ID.
        Notes:
            This function modifies the state of a task stage by interacting with the
            `core.assets` module. Ensure that the `core.assets` module is properly
            configured and accessible.
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            core.assets.modify_stage_state(stage_id, state, comment)

    def estimate_task_time(self, stage, time):
        """
        Estimate and update the task time for a given stage.
        This method takes a stage identifier (either as a string or directly as an ID)
        and updates its estimated time in the system.
        Args:
            stage (str or int): The stage identifier. If a string is provided, it will
            be converted to an instance type and stage ID. If an integer is provided,
            it is assumed to be the stage ID directly.
            time (float or int): The estimated time to be set for the stage.
        Returns:
            None
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            core.assets.modify_stage_estimation(stage_id, time)

    def add_task_comment(self, stage, comment):
        """
        Adds a comment to a specific task stage.
        Args:
            stage (str or int): The stage identifier. It can be a string representing 
                the stage (which will be converted to an instance and stage ID) or 
                an integer representing the stage ID directly.
            comment (str): The comment to be added to the specified stage.
        Returns:
            None
        """

        if type(stage) == str:
            instance_type, stage_id = core.assets.string_to_instance(stage)
        else:
            stage_id = stage

        if stage_id:
            core.assets.add_stage_comment(stage_id, comment)


class launch:
    """
    A class to manage and control work environment-related software instances.
    Methods:
        __init__():
            Initializes the launch class.
        work_env(work_env):
            Runs the last version of the given work environment-related software.
            Args:
                work_env (str or int): The work environment identifier or name.
        work_version(work_version):
            Runs the given work version-related software.
            Args:
                work_version (str or int): The work version identifier or name.
        kill_work_env(work_env):
            Terminates the given work environment-related software instance.
            Args:
                work_env (str or int): The work environment identifier or name.
        kill_all():
            Terminates all the running work environment-related software instances.
        get_running_work_envs():
            Returns a list of running work environment-related software instances.
            Returns:
                list: A list of running work environment identifiers as strings.
        lock_work_env(work_env):
            Locks the given work environment for the current user.
            Args:
                work_env (str or int): The work environment identifier or name.
        unlock_work_env(work_env):
            Unlocks the given work environment if it is locked by the current user.
            Args:
                work_env (str or int): The work environment identifier or name.
        unlock_all():
            Unlocks all the work environments locked by the current user.
    """

    def __init__(self):
        pass

    def work_env(self, work_env):
        """
        Sets the work environment and launches the last work version if available.
        Args:
            work_env (str or int): The work environment identifier. It can be a string
                representing the work instance or an integer representing the work environment ID.
        Behavior:
            - If `work_env` is a string, it is converted to a work environment ID using
              `core.assets.string_to_work_instance`.
            - If a valid work environment ID is obtained, the function retrieves the last
              work version ID associated with it using `core.project.get_last_work_version`.
            - If a last work version ID exists, it launches the corresponding work version
              using `core.launch.launch_work_version`.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            last_work_version_id = core.project.get_last_work_version(
                work_env_id, 'id')
            if last_work_version_id:
                core.launch.launch_work_version(last_work_version_id[0])

    def work_version(self, work_version):
        """
        Executes the software associated with the given work version.
        Args:
            work_version (str or int): The work version to be processed. If a string is provided, 
                                       it will be converted to a work version ID. If an integer 
                                       (work version ID) is provided, it will be used directly.
        Returns:
            None
        Raises:
            ValueError: If the provided work_version is invalid or cannot be processed.
        Notes:
            - If `work_version` is a string, it is parsed into an instance type and work version ID.
            - If `work_version` is an integer, it is assumed to be the work version ID.
            - The function launches the corresponding work version using the core.launch module.
        """

        if type(work_version) == str:
            instance_type, work_version_id = core.assets.string_to_work_instance(
                work_version)
        else:
            work_version_id = work_version

        if work_version_id:
            core.launch.launch_work_version(work_version_id)

    def kill_work_env(self, work_env):
        """
        Terminates a specified work environment.
        Args:
            work_env (str or int): The work environment to terminate. If a string is 
                provided, it will be converted to a work environment ID. If an integer 
                is provided, it is assumed to be the work environment ID directly.
        Raises:
            None: This function does not explicitly raise exceptions, but errors may 
            occur if the provided work environment is invalid or if the termination 
            process fails.
        Notes:
            - The function uses `core.assets.string_to_work_instance` to parse the 
              string representation of the work environment into its type and ID.
            - The termination process is handled by `core.launch.kill` using the 
              resolved work environment ID.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            core.launch.kill(work_env_id)

    def kill_all(self):
        """
        Terminates all running work environments managed by the application.

        This method calls the `kill_all` function from the `core.launch` module
        to ensure that all active work environments are forcefully stopped.

        Raises:
            Exception: If an error occurs while attempting to terminate processes.
        """
        core.launch.kill_all()

    def get_running_work_envs(self):
        """
        Retrieves a list of currently running work environments.

        This function fetches the IDs of running work environments using 
        `core.launch.get()` and converts them into string representations 
        using `core.assets.instance_to_string`.

        Returns:
            list: A list of string representations of running work environments.
        """
        running_work_envs = []
        running_work_env_ids = core.launch.get()
        if running_work_env_ids:
            for work_env_id in running_work_env_ids:
                running_work_envs.append(core.assets.instance_to_string(('work_env',
                                                                         work_env_id)))
        return running_work_envs

    def lock_work_env(self, work_env):
        """
        Locks the specified work environment by setting a lock flag.
        Args:
            work_env (str or int): The work environment to lock. It can be either:
                - A string representing the work environment, which will be 
                  converted to an instance type and ID using 
                  `core.assets.string_to_work_instance`.
                - An integer representing the work environment ID directly.
        Returns:
            None
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            core.project.set_work_env_lock(work_env_id, 1)

    def unlock_work_env(self, work_env):
        """
        Unlocks the specified work environment by removing its lock.
        Args:
            work_env (str or int): The work environment to unlock. It can be 
                provided as a string representing the work instance or as an 
                integer representing the work environment ID.
        Raises:
            ValueError: If the provided `work_env` is neither a string nor an integer.
        Notes:
            - If `work_env` is a string, it will be converted to a work environment ID 
              using `core.assets.string_to_work_instance`.
            - The lock is removed by setting the work environment's lock status to 0 
              using `core.project.set_work_env_lock`.
        """
        if type(work_env) == str:
            instance_type, work_env_id = core.assets.string_to_work_instance(
                work_env)
        else:
            work_env_id = work_env

        if work_env_id:
            core.project.set_work_env_lock(work_env_id, 0)

    def unlock_all(self):
        """
        Unlocks all locked work environments in the current project.

        This method calls the `unlock_all` function from the `core.project` module
        to release any locks on work environments, making them available for modification
        or access.

        Usage:
            Call this method to ensure all work environments in the project are unlocked.

        """
        core.project.unlock_all()


class team:
    def __init__(self):
        pass

    def refresh_ui(self):
        """
        Refreshes the team users interfaces.

        This method checks if the current user has associated team DNS information.
        If team DNS information is available, it triggers a refresh of the team
        interfaces using the team client and environment modules.

        Returns:
            None
        """
        if core.user.user().get_team_dns():
            core.team_client.refresh_team(core.environment.get_team_dns())

    def set_team_DNS(self, host, port):
        """
        Configures the DNS settings for a team by specifying the host and port.

        Args:
            host (str): The DNS host address to be set.
            port (int): The port number associated with the DNS host.

        Returns:
            None
        """
        core.user.user().set_team_dns(host, port)

    def get_team_dns(self):
        """
        Retrieves the team DNS (Domain Name System) information.

        Returns:
            str or None: The team DNS as a string if available, otherwise None.
        """
        if core.user.user().get_team_dns():
            return core.environment.get_team_dns()
        else:
            return None


class ui:
    """
    A class that provides an interface for interacting with the wizard's GUI.
    Methods:
        is_gui():
            Checks if the wizard GUI is currently open.
            Returns True if the GUI is open, False otherwise.
        raise_ui():
            Brings the wizard window to the foreground.
        restart_ui():
            Restarts the wizard interface.
        refresh_ui():
            Refreshes the wizard interface.
        focus_asset(asset):
            Focuses on the specified asset in the project tree.
            Args:
                asset (str or int): The asset to focus on. Can be a string representation
                or an asset ID.
        focus_stage(stage):
            Focuses on the specified stage in the project tree.
            Args:
                stage (str or int): The stage to focus on. Can be a string representation
                or a stage ID.
        focus_variant(variant):
            Focuses on the specified variant in the wizard.
            Args:
                variant (str or int): The variant to focus on. Can be a string representation
                or a variant ID.
        focus_work_version(work_version):
            Focuses on the specified work version in the work versions tab.
            Args:
                work_version (str or int): The work version to focus on. Can be a string representation
                or a work version ID.
    """

    def __init__(self):
        pass

    def is_gui(self):
        """
        Checks if the wizard GUI is currently open.

        This method determines whether the wizard is running in GUI mode
        or in a command-line interface (CLI) mode such as PyWizard or Wizard_CMD.

        Returns:
            bool: True if the wizard GUI is open, False otherwise.
        """
        return core.environment.is_gui()

    def raise_ui(self):
        """
        Raises the wizard window by invoking the GUI server's raise_ui method.

        This method is used to bring the wizard's graphical user interface (GUI)
        to the foreground, ensuring it is visible to the user.

        Dependencies:
            - Requires the `gui.gui_server.raise_ui` method to be implemented and accessible.

        Raises:
            None
        """
        gui.gui_server.raise_ui()

    def restart_ui(self):
        """
        Restarts the wizard interface.

        This method stops and then starts the wizard's graphical user interface (GUI),
        effectively restarting it. This can be useful for applying changes or resolving
        issues without needing to restart the entire application.

        Dependencies:
            - Requires the `gui.gui_server.restart_ui` method to be implemented and accessible.

        Raises:
            None
        """
        gui.gui_server.restart_ui()

    def refresh_ui(self):
        """
        Refreshes the wizard interface.

        This method triggers the GUI server to refresh the wizard's graphical
        user interface (GUI). It can be used to update the interface after
        changes have been made to the underlying data or settings.

        Dependencies:
            - Requires the `gui.gui_server.refresh_ui` method to be implemented
              and accessible.

        Raises:
            None
        """
        gui.gui_server.refresh_ui()

    def focus_asset(self, asset):
        """
        Focuses on the specified asset in the project tree.

        Args:
            asset (str or int): The asset to focus on. Can be provided as:
                - A string representing the asset, which will be converted to an instance type and ID.
                - An integer representing the asset ID directly.

        Behavior:
            - If the asset is provided as a string, it is parsed into an instance type and ID using `core.assets.string_to_instance`.
            - If the asset is provided as an integer, it is assumed to be the asset ID.
            - If the instance type is 'asset', the function calls `gui.gui_server.focus_instance` to focus on the specified asset.

        Notes:
            - This function interacts with the GUI server to update the focus in the project tree.
            - Ensure that the `core.assets` and `gui.gui_server` modules are properly configured and accessible.

        Raises:
            None
        """
        if type(asset) == str:
            instance_type, instance_id = core.assets.string_to_instance(asset)
        else:
            instance_type = 'asset'
            instance_id = asset

        if instance_type == 'asset':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_stage(self, stage):
        """
        Focuses on the specified stage in the project tree.
        Args:
            stage (str or int): The stage to focus on. If a string is provided, it is 
                converted to an instance type and ID using `core.assets.string_to_instance`. 
                If an integer is provided, it is assumed to be the stage ID.
        Behavior:
            - If the `stage` is a string, it is parsed into an instance type and ID.
            - If the `stage` is not a string, it is assumed to be a stage ID with the 
              instance type set to 'stage'.
            - The function then calls `gui.gui_server.focus_instance` to focus on the 
              specified instance in the GUI.
        Note:
            This function assumes the existence of `core.assets.string_to_instance` for 
            parsing strings into instance types and IDs, and `gui.gui_server.focus_instance` 
            for interacting with the GUI.
        """
        if type(stage) == str:
            instance_type, instance_id = core.assets.string_to_instance(stage)
        else:
            instance_type = 'stage'
            instance_id = stage

        if instance_type == 'stage':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_variant(self, variant):
        """
        Focuses on the specified variant in the wizard interface.
        Args:
            variant (str or int): The variant to focus on. If a string is 
            provided, it will be converted to an instance type and ID 
            using `core.assets.string_to_instance`. If an integer is 
            provided, it is assumed to be the variant ID.
        Behavior:
            - If the `variant` is a string, it is parsed into an instance 
              type and ID.
            - If the `variant` is not a string, it is assumed to be a 
              variant ID with the instance type set to 'variant'.
            - The function then instructs the GUI server to focus on the 
              specified instance.
        Raises:
            None
        """
        if type(variant) == str:
            instance_type, instance_id = core.assets.string_to_instance(
                variant)
        else:
            instance_type = 'variant'
            instance_id = variant

        if instance_type == 'variant':
            gui.gui_server.focus_instance((instance_type, instance_id))

    def focus_work_version(self, work_version):
        """
        Focuses on the specified work version in the work versions tab.
        Args:
            work_version (str or int): The work version to focus on. If a string is 
                provided, it will be converted to an instance type and ID using 
                `core.assets.string_to_work_instance`. If an integer is provided, 
                it is assumed to be the ID of a work version.
        Behavior:
            - If `work_version` is a string, it is parsed into an instance type 
              and ID.
            - If `work_version` is not a string, it is assumed to be a work version 
              ID with the instance type set to 'work_version'.
            - If the instance type is 'work_version', the function will call 
              `gui.gui_server.focus_work_version` with the instance ID to focus 
              on the specified work version.
        """
        if type(work_version) == str:
            instance_type, instance_id = core.assets.string_to_work_instance(
                work_version)
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
