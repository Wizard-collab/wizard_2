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
This module provides functionality for managing user preferences, sessions, 
and project environments in the Wizard application. It includes classes and 
functions for handling user-specific configurations, logging in and out of 
projects, and executing scripts within a session context.

Key Features:
- User preference management, including database connections, repositories, 
    widget positions, and filter sets.
- Session initialization and script execution.
- Project login and environment setup.
- Dependency analysis for Python scripts to identify forbidden modules.

Dependencies:
- Python modules: yaml, ast, importlib, sys, logging
- Wizard modules: user_vars, tools, path_utils, environment, project, 
    repository, db_core, db_utils, team_client
"""

# Python modules
import yaml
import ast
import importlib
import sys
import logging

# Wizard modules
from wizard.vars import user_vars
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import environment
from wizard.core import project
from wizard.core import repository
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import team_client

logger = logging.getLogger(__name__)


def create_user_folders():
    """
    Creates necessary user directories and updates the system path.

    This function ensures that the required directories for the user are created
    if they do not already exist. It also appends the user's script path to the
    system path for module resolution.

    Directories created:
    - The script path directory specified in `user_vars._script_path_`.
    - The icons path directory specified in `user_vars._icons_path_`.

    Dependencies:
    - `path_utils.makedirs`: Used to create directories.
    - `sys.path.append`: Used to add the script path to the system path.

    Note:
    - Ensure that `user_vars._script_path_` and `user_vars._icons_path_` are
      properly defined before calling this function.
    """
    path_utils.makedirs(user_vars._script_path_)
    sys.path.append(user_vars._script_path_)
    path_utils.makedirs(user_vars._icons_path_)


def init_user_session():
    """
    Initializes a new user session by clearing the session file and 
    importing the session module.

    This function performs the following steps:
    1. Opens the session file (defined in `user_vars._session_file_`) in write mode
       and clears its contents by writing an empty string.
    2. Imports the `session` module, which may be responsible for managing 
       session-related functionality.

    Note:
    - Ensure that `user_vars._session_file_` is properly defined and points to 
      a valid file path before calling this function.
    - The `session` module must be available and accessible for import.
    """
    with open(user_vars._session_file_, 'w') as f:
        f.write('')


create_user_folders()
init_user_session()
import session  # noqa: E402


class user:
    """
    This module defines the `user` class, which manages user preferences and settings 
    for the application. It provides methods to set, retrieve, and manipulate various 
    user-specific configurations such as database connections, repositories, widget 
    positions, filter sets, and application settings.
    Classes:
        user:
            A class to handle user preferences and settings, including database 
            connections, repositories, widget positions, filter sets, and other 
            application-specific configurations.
    Methods:
        __init__():
            Initializes the user class and loads user preferences from a file.
        set_psql_dns(host, port, user, password):
            Sets the PostgreSQL DNS connection string and updates the environment.
        get_psql_dns():
            Retrieves the PostgreSQL DNS connection string and validates the connection.
        get_repository():
            Retrieves the currently set repository.
        set_repository(repository):
            Sets the repository name after validating its format.
        set_team_dns(host, port):
            Sets the team server DNS and updates the environment.
        get_team_dns():
            Retrieves the team server DNS and validates the connection.
        set_widget_pos(widget_name, pos_dic):
            Sets the position of a widget in the user preferences.
        get_widget_pos(widget_name):
            Retrieves the position of a widget from the user preferences.
        add_filter_set(widget_name, filter_name, filter_dic):
            Adds a new filter set for a widget.
        edit_filter_set(widget_name, filter_name, filter_dic):
            Edits an existing filter set for a widget.
        get_filters_sets(widget_name):
            Retrieves all filter sets for a widget.
        get_filter_set(widget_name, filter_name):
            Retrieves a specific filter set for a widget.
        delete_filter_set(widget_name, filter_name):
            Deletes a specific filter set for a widget.
        add_context(type, context_dic):
            Adds a context dictionary for a specific type.
        get_context(type):
            Retrieves the context dictionary for a specific type.
        add_recent_scene(work_env_tuple):
            Adds a recent scene to the user's preferences.
        get_recent_scenes():
            Retrieves the list of recent scenes for the current project.
        get_show_splash_screen():
            Checks if the splash screen should be shown.
        set_show_splash_screen(show_splash_screen):
            Sets whether the splash screen should be shown.
        get_show_latest_build():
            Checks if the latest build notification should be shown.
        set_show_latest_build(show_latest_build):
            Sets whether the latest build notification should be shown.
        set_local_path(path):
            Sets the local path for the user.
        set_reference_auto_update_default(auto_update_default=False):
            Sets the default auto-update setting for references.
        get_reference_auto_update_default():
            Retrieves the default auto-update setting for references.
        set_popups_settings(enabled=1, blink=1, duration=3, keep_until_comment=True):
            Configures popup notification settings.
        get_popups_enabled():
            Checks if popups are enabled.
        get_popups_blink_enabled():
            Checks if popup blinking is enabled.
        get_app_scale():
            Retrieves the application scale setting.
        set_app_scale(app_scale):
            Sets the application scale setting.
        get_keep_until_comment():
            Checks if popups should be kept until a comment is made.
        get_popups_duration():
            Retrieves the duration for which popups are displayed.
        get_local_path():
            Retrieves the local path for the user.
        get_user_build():
            Retrieves the user's build setting.
        set_user_build(build):
            Sets the user's build setting.
        get_user_prefs_dic():
            Loads the user preferences dictionary from a file or initializes it.
        write_prefs_dic():
            Writes the user preferences dictionary to a file.
        execute_session(script):
            Executes a Python script in the context of the current session.
        execute_py(file):
            Executes a Python script from a file.
    """

    def __init__(self):
        """
        Initializes the user object and retrieves user preferences.

        This constructor method calls the `get_user_prefs_dic` function
        to load the user's preferences into the object.
        """
        self.get_user_prefs_dic()

    def set_psql_dns(self, host, port, user, password):
        """
        Configures and sets the PostgreSQL Data Source Name (DSN) for the application.

        This method constructs a DSN string using the provided host, port, user, and password.
        It attempts to establish a connection using the constructed DSN. If the connection
        is successful, it updates the user's preferences dictionary with the DSN and resets
        the repository preference. The updated preferences are then saved, and the DSN is
        set in the application's environment.

        Args:
            host (str): The hostname or IP address of the PostgreSQL server.
            port (int): The port number on which the PostgreSQL server is listening.
            user (str): The username to authenticate with the PostgreSQL server.
            password (str): The password to authenticate with the PostgreSQL server.

        Returns:
            int: Returns 1 if the DSN is successfully set and the connection is valid.
                 Returns None if the connection attempt fails.
        """
        DNS = f"host={host} port={port} user={user} password={password}"
        if not db_core.try_connection(DNS):
            return
        self.prefs_dic[user_vars._psql_dns_] = DNS
        self.prefs_dic[user_vars._repository_] = None
        self.write_prefs_dic()
        environment.set_psql_dns(DNS)
        return 1

    def get_psql_dns(self):
        """
        Retrieves and validates the PostgreSQL DNS (Data Source Name) from the user's preferences.

        This function performs the following steps:
        1. Checks if the PostgreSQL DNS is set in the user's preferences. If not, logs a message and exits.
        2. Attempts to establish a connection using the provided DNS. If the connection fails:
           - Resets the DNS value in the preferences to None.
           - Writes the updated preferences to persist the change.
           - Exits the function.
        3. If the connection is successful, sets the DNS in the environment for further use.

        Returns:
            int: Returns 1 if the DNS is successfully validated and set.
            None: Returns None if the DNS is not set or the connection fails.
        """
        if not self.prefs_dic[user_vars._psql_dns_]:
            logger.info("No postgreSQL DNS set")
            return
        if not db_core.try_connection(self.prefs_dic[user_vars._psql_dns_]):
            self.prefs_dic[user_vars._psql_dns_] = None
            self.write_prefs_dic()
            return
        environment.set_psql_dns(self.prefs_dic[user_vars._psql_dns_])
        return 1

    def get_repository(self):
        """
        Retrieves the repository path from the user's preferences and sets it in the environment.

        If no repository is defined in the user's preferences, logs an informational message
        and returns without performing any action. Otherwise, sets the repository in the
        environment and returns a success indicator.

        Returns:
            int or None: Returns 1 if the repository is successfully set, otherwise None.
        """
        if not self.prefs_dic[user_vars._repository_]:
            logger.info("No repository defined")
            return
        environment.set_repository(self.prefs_dic[user_vars._repository_])
        return 1

    def set_repository(self, repository):
        """
        Sets the repository name for the user preferences and updates the environment.

        Args:
            repository (str): The name of the repository to set. It must be a non-empty string
                              containing only lowercase characters, numbers, and underscores.

        Returns:
            int or None: Returns 1 if the repository is successfully set. Returns None if the 
                         repository is invalid or not provided.

        Logs:
            - Logs a warning if the repository name is None or an empty string.
            - Logs a warning if the repository name contains invalid characters.
        """
        if (repository is None) or (repository == ''):
            logger.warning(f'Please provide a repository name')
            return
        if not tools.is_dbname_safe(repository):
            logger.warning(
                f'Please enter a repository name with only lowercase characters, numbers and "_"')
            return
        self.prefs_dic[user_vars._repository_] = repository
        environment.set_repository(self.prefs_dic[user_vars._repository_])
        self.write_prefs_dic()
        return 1

    def set_team_dns(self, host, port):
        """
        Sets the team DNS (Domain Name System) configuration and updates the preferences.

        Args:
            host (str): The hostname or IP address of the DNS server.
            port (int): The port number of the DNS server.

        Returns:
            int: Returns 1 after successfully modifying the team DNS.

        Raises:
            None

        Logs:
            - Logs a warning if the DNS server cannot be reached.
            - Logs an info message when the team DNS is successfully modified.

        Side Effects:
            - Updates the `prefs_dic` dictionary with the new DNS configuration.
            - Writes the updated preferences to persistent storage.
            - Updates the environment with the new DNS configuration.
        """
        DNS = (host, port)
        if not team_client.try_connection(DNS):
            logger.warning("Can't reach server with this DNS")
        self.prefs_dic[user_vars._team_dns_] = DNS
        self.write_prefs_dic()
        environment.set_team_dns(DNS)
        logger.info("Team DNS modified")
        return 1

    def get_team_dns(self):
        """
        Retrieves and sets the team DNS (Domain Name System) for the user.

        This function checks if the user's preferences contain a team DNS. If no team DNS is set,
        it logs an informational message and exits. If a team DNS is set but the connection to the
        team server cannot be established, it logs the issue and updates the environment with the
        provided DNS. If the connection is successful, it sets the team DNS in the environment.

        Returns:
            int or None: Returns 1 if the team DNS is successfully set and reachable. 
                         Returns None if no team DNS is set or if the connection fails.
        """
        if not self.prefs_dic[user_vars._team_dns_]:
            logger.info("No team DNS set")
            return
        if not team_client.try_connection(self.prefs_dic[user_vars._team_dns_]):
            environment.set_team_dns(self.prefs_dic[user_vars._team_dns_])
            logger.info(
                f"Can't reach team server with this DNS : {self.prefs_dic[user_vars._team_dns_]}")
            return
        environment.set_team_dns(self.prefs_dic[user_vars._team_dns_])
        return 1

    def set_widget_pos(self, widget_name, pos_dic):
        """
        Updates the position of a specified widget in the user's preferences and saves the updated preferences.

        Args:
            widget_name (str): The name of the widget whose position is being updated.
            pos_dic (dict): A dictionary containing the position data for the widget.

        Side Effects:
            Updates the `prefs_dic` attribute with the new widget position.
            Calls `write_prefs_dic` to persist the updated preferences to storage.
        """
        self.prefs_dic[user_vars._widgets_pos_][widget_name] = pos_dic
        self.write_prefs_dic()

    def get_widget_pos(self, widget_name):
        """
        Retrieve the position of a specified widget from the user's preferences.

        Args:
            widget_name (str): The name of the widget whose position is to be retrieved.

        Returns:
            The position of the widget if it exists in the user's preferences; 
            otherwise, None.
        """
        if widget_name not in self.prefs_dic[user_vars._widgets_pos_].keys():
            return
        return self.prefs_dic[user_vars._widgets_pos_][widget_name]

    def add_filter_set(self, widget_name, filter_name, filter_dic):
        """
        Adds a new filter set to the preferences dictionary for a specific widget.

        Args:
            widget_name (str): The name of the widget to which the filter set belongs.
            filter_name (str): The name of the filter set to be added.
            filter_dic (dict): A dictionary containing the filter set's configuration.

        Returns:
            None: If the filter name is not safe or already exists.
            Any: The result of the `edit_filter_set` method if the filter set is successfully created.

        Logs:
            - A warning if the filter set already exists for the widget.
            - An info message if the filter set is successfully created.
        """
        if not tools.is_safe(filter_name):
            return
        if 'filter_sets' not in self.prefs_dic.keys():
            self.prefs_dic['filter_sets'] = dict()
        if widget_name not in self.prefs_dic['filter_sets'].keys():
            self.prefs_dic['filter_sets'][widget_name] = dict()
        if filter_name in self.prefs_dic['filter_sets'][widget_name].keys():
            logger.warning(f"{filter_name} already exists")
            return
        logger.info(f"{filter_name} created")
        return self.edit_filter_set(widget_name, filter_name, filter_dic)

    def edit_filter_set(self, widget_name, filter_name, filter_dic):
        """
        Edits or creates a filter set for a specific widget and saves the preferences.

        Args:
            widget_name (str): The name of the widget for which the filter set is being edited or created.
            filter_name (str): The name of the filter set to be edited or created.
            filter_dic (dict): A dictionary containing the filter configuration.

        Returns:
            int: Always returns 1 to indicate successful execution.

        Side Effects:
            - Updates the `prefs_dic` attribute with the new or modified filter set.
            - Writes the updated preferences to persistent storage by calling `write_prefs_dic`.
            - Logs an informational message indicating the filter set has been edited.
        """
        if 'filter_sets' not in self.prefs_dic.keys():
            self.prefs_dic['filter_sets'] = dict()
        if widget_name not in self.prefs_dic['filter_sets'].keys():
            self.prefs_dic['filter_sets'][widget_name] = dict()
        self.prefs_dic['filter_sets'][widget_name][filter_name] = filter_dic
        self.write_prefs_dic()
        logger.info(f"{filter_name} edited")
        return 1

    def get_filters_sets(self, widget_name):
        """
        Retrieves or initializes the filter sets for a given widget.

        This method ensures that the `filter_sets` dictionary exists within the 
        `prefs_dic` attribute. If the specified `widget_name` does not have an 
        associated filter set, it initializes an empty dictionary for it.

        Args:
            widget_name (str): The name of the widget for which to retrieve or 
                               initialize the filter sets.

        Returns:
            dict: The filter sets associated with the specified widget.
        """
        if 'filter_sets' not in self.prefs_dic.keys():
            self.prefs_dic['filter_sets'] = dict()
        if widget_name not in self.prefs_dic['filter_sets']:
            self.prefs_dic['filter_sets'][widget_name] = dict()
        return self.prefs_dic['filter_sets'][widget_name]

    def get_filter_set(self, widget_name, filter_name):
        """
        Retrieves a specific filter set from the preferences dictionary.

        Args:
            widget_name (str): The name of the widget for which the filter set is being retrieved.
            filter_name (str): The name of the filter set to retrieve.

        Returns:
            dict or None: The filter set dictionary if found, otherwise None.

        Notes:
            - If the 'filter_sets' key does not exist in the preferences dictionary, it will be initialized as an empty dictionary.
            - If the specified widget_name does not exist under 'filter_sets', it will also be initialized as an empty dictionary.
            - If the specified filter_name does not exist under the widget_name, a warning will be logged, and None will be returned.
        """
        if 'filter_sets' not in self.prefs_dic.keys():
            self.prefs_dic['filter_sets'] = dict()
        if widget_name not in self.prefs_dic['filter_sets'].keys():
            self.prefs_dic['filter_sets'][widget_name] = dict()
        if filter_name not in self.prefs_dic['filter_sets'][widget_name].keys():
            logger.warning(f"{filter_name} not found")
            return
        return self.prefs_dic['filter_sets'][widget_name][filter_name]

    def delete_filter_set(self, widget_name, filter_name):
        """
        Deletes a specific filter set associated with a widget from the preferences dictionary.

        Args:
            widget_name (str): The name of the widget whose filter set is to be deleted.
            filter_name (str): The name of the filter set to delete.

        Returns:
            int: Returns 1 if the filter set is successfully deleted.

        Logs:
            - Logs a warning if the filter set is not found.
            - Logs an info message when the filter set is successfully deleted.

        Side Effects:
            - Modifies the `prefs_dic` attribute by removing the specified filter set.
            - Calls `write_prefs_dic()` to persist changes to the preferences dictionary.
        """
        if 'filter_sets' not in self.prefs_dic.keys():
            self.prefs_dic['filter_sets'] = dict()
        if widget_name not in self.prefs_dic['filter_sets'].keys():
            self.prefs_dic['filter_sets'][widget_name] = dict()
        if filter_name not in self.prefs_dic['filter_sets'][widget_name].keys():
            logger.warning(f"{filter_name} not found")
            return
        del self.prefs_dic['filter_sets'][widget_name][filter_name]
        self.write_prefs_dic()
        logger.info(f"{filter_name} deleted")
        return 1

    def add_context(self, type, context_dic):
        """
        Adds a context dictionary to the preferences dictionary for a specified type and project.

        Args:
            type (str): The type/category to which the context dictionary belongs.
            context_dic (dict): The context dictionary to be added.

        Behavior:
            - If the specified type does not exist in the preferences dictionary, it initializes it as an empty dictionary.
            - Associates the context dictionary with the current project name under the specified type.
            - Updates the preferences dictionary by writing the changes to persistent storage.

        Dependencies:
            - Relies on `environment.get_project_name()` to retrieve the current project name.
            - Calls `self.write_prefs_dic()` to persist the updated preferences dictionary.
        """
        if type not in self.prefs_dic.keys():
            self.prefs_dic[type] = dict()
        self.prefs_dic[type][environment.get_project_name()] = context_dic
        self.write_prefs_dic()

    def get_context(self, type):
        """
        Retrieve the context value for a given type and the current project.

        Args:
            type (str): The type of context to retrieve.

        Returns:
            Any: The context value associated with the given type and the current project,
             or None if the type or project is not found in the preferences dictionary.
        """
        if type not in self.prefs_dic.keys():
            return
        if environment.get_project_name() not in self.prefs_dic[type].keys():
            return
        return self.prefs_dic[type][environment.get_project_name()]

    def add_recent_scene(self, work_env_tuple):
        """
        Adds a recent work environment tuple to the user's preferences dictionary.

        This function manages a list of recent work environments for a specific project.
        It ensures that the list does not exceed a maximum of 5 entries, removes duplicates,
        and appends the new work environment tuple to the list. The updated preferences
        dictionary is then saved.

        Args:
            work_env_tuple (tuple): A tuple representing the work environment to be added.
                                    The first element of the tuple is used to check for duplicates.

        Behavior:
            - If the recent work environments key does not exist in the preferences dictionary,
              it initializes it.
            - If the project name is not present under the recent work environments key,
              it initializes an empty list for that project.
            - Ensures the list of recent work environments for the project does not exceed
              5 entries by removing the oldest entries.
            - Removes any existing tuple in the list that matches the first element of the
              provided tuple.
            - Appends the new work environment tuple to the list.
            - Saves the updated preferences dictionary by calling `self.write_prefs_dic()`.
        """
        if user_vars._recent_work_envs_ not in self.prefs_dic.keys():
            self.prefs_dic[user_vars._recent_work_envs_] = dict()
        if environment.get_project_name() not in self.prefs_dic[user_vars._recent_work_envs_].keys():
            self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()] = [
            ]
        while len(self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()]) > 4:
            self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()].pop(
                0)
            print(self.prefs_dic[user_vars._recent_work_envs_]
                  [environment.get_project_name()])
        for existing_tuple in self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()]:
            if work_env_tuple[0] == existing_tuple[0]:
                self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()].remove(
                    existing_tuple)
        self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()].append(
            work_env_tuple)
        self.write_prefs_dic()

    def get_recent_scenes(self):
        """
        Retrieves the list of recent scenes for the current project.

        This function checks the user's preferences dictionary to find the recent
        work environments associated with the current project. If no recent work
        environments or project-specific data exist, it returns an empty list.

        Returns:
            list: A list of recent scenes for the current project, or an empty list
            if no data is available.
        """
        if user_vars._recent_work_envs_ not in self.prefs_dic.keys():
            return []
        if environment.get_project_name() not in self.prefs_dic[user_vars._recent_work_envs_].keys():
            return []
        return self.prefs_dic[user_vars._recent_work_envs_][environment.get_project_name()]

    def get_show_splash_screen(self):
        """
        Retrieves the user's preference for showing the splash screen.

        If the preference key for showing the splash screen does not exist in 
        the preferences dictionary, it sets the default value to True.

        Returns:
            bool: The user's preference for showing the splash screen.
        """
        if user_vars._show_splash_screen_ not in self.prefs_dic.keys():
            self.set_show_splash_screen(True)
        return self.prefs_dic[user_vars._show_splash_screen_]

    def set_show_splash_screen(self, show_splash_screen):
        """
        Updates the user's preference for showing the splash screen and saves the updated preferences.

        Args:
            show_splash_screen (bool): A boolean value indicating whether the splash screen should be shown (True) or not (False).

        Side Effects:
            Updates the `prefs_dic` dictionary with the new splash screen preference.
            Writes the updated preferences to persistent storage by calling `write_prefs_dic()`.
        """
        self.prefs_dic[user_vars._show_splash_screen_] = show_splash_screen
        self.write_prefs_dic()

    def get_show_latest_build(self):
        """
        Retrieves the user's preference for showing the latest build.

        If the preference key `_show_latest_build_` is not present in the 
        `prefs_dic` dictionary, it initializes the preference to `True` 
        by calling `set_show_latest_build`.

        Returns:
            bool: The current value of the `_show_latest_build_` preference.
        """
        if user_vars._show_latest_build_ not in self.prefs_dic.keys():
            self.set_show_latest_build(True)
        return self.prefs_dic[user_vars._show_latest_build_]

    def set_show_latest_build(self, show_latest_build):
        """
        Updates the user's preference for showing the latest build notification 
        and saves the updated preferences.

        Args:
            show_latest_build (bool): A boolean value indicating whether the 
                                      latest build notification should be shown (True) or not (False).

        Side Effects:
            - Updates the `prefs_dic` dictionary with the new preference.
            - Persists the updated preferences to storage by calling `write_prefs_dic()`.

        """
        self.prefs_dic[user_vars._show_latest_build_] = show_latest_build
        self.write_prefs_dic()

    def set_local_path(self, path):
        """
        Sets the local path for the user preferences.

        Args:
            path (str): The local path to be set. Must be a valid directory path.

        Returns:
            int: Returns 1 if the local path is successfully modified.
                 Returns None if the path is invalid.

        Logs:
            - Logs a warning if the provided path is empty or invalid.
            - Logs an info message when the local path is successfully modified.
        """
        if path == '' or not path_utils.isdir(path):
            logger.warning('Please enter a valid local path')
            return
        self.prefs_dic[user_vars._local_path_] = path_utils.clean_path(path)
        self.write_prefs_dic()
        logger.info("Local path modified")
        return 1

    def set_reference_auto_update_default(self, auto_update_default=False):
        """
        Sets the default value for the 'auto_update_default' setting in the user's preferences.

        This method checks if the '_reference_settings_' key exists in the preferences dictionary.
        If it does not exist, it initializes it as an empty dictionary. Then, it sets the 
        'auto_update_default' key within the '_reference_settings_' dictionary to the provided value.
        Finally, it writes the updated preferences dictionary to persist the changes.

        Args:
            auto_update_default (bool, optional): The default value for the 'auto_update_default' 
                setting. Defaults to False.
        """
        if user_vars._reference_settings_ not in self.prefs_dic.keys():
            self.prefs_dic[user_vars._reference_settings_] = dict()
        self.prefs_dic[user_vars._reference_settings_]['auto_update_default'] = auto_update_default
        self.write_prefs_dic()

    def get_reference_auto_update_default(self):
        """
        Retrieves the default setting for automatic reference updates.

        If the `_reference_settings_` key is not present in the `prefs_dic` dictionary,
        it initializes the default setting by calling `set_reference_auto_update_default`.

        Returns:
            bool: The value of the 'auto_update_default' setting from the `prefs_dic` dictionary.
        """
        if user_vars._reference_settings_ not in self.prefs_dic.keys():
            self.set_reference_auto_update_default()
        return self.prefs_dic[user_vars._reference_settings_]['auto_update_default']

    def set_popups_settings(self, enabled=1, blink=1, duration=3, keep_until_comment=True):
        """
        Configure the settings for popups.

        Args:
            enabled (int, optional): Determines if popups are enabled. 
                Defaults to 1 (enabled).
            blink (int, optional): Specifies whether the popup should blink. 
                Defaults to 1 (blink enabled).
            duration (int, optional): Duration (in seconds) for which the popup 
                should be displayed. Defaults to 3 seconds.
            keep_until_comment (bool, optional): If True, the popup will remain 
                visible until a comment is made. Defaults to True.

        Updates:
            Updates the `prefs_dic` dictionary with the popup settings and 
            writes the updated preferences to persistent storage.
        """
        popups_settings_dic = dict()
        popups_settings_dic['enabled'] = enabled
        popups_settings_dic['blink'] = blink
        popups_settings_dic['duration'] = duration
        popups_settings_dic['keep_until_comment'] = keep_until_comment
        self.prefs_dic[user_vars._popups_settings_] = popups_settings_dic
        self.write_prefs_dic()

    def get_popups_enabled(self):
        """
        Retrieve the status of whether popups are enabled for the user.

        Returns:
            bool: True if popups are enabled, False otherwise.
        """
        return self.prefs_dic[user_vars._popups_settings_]['enabled']

    def get_popups_blink_enabled(self):
        """
        Retrieve the blink setting for popups from the user's preferences.

        This method checks if the 'blink' key exists in the user's popup settings
        within the preferences dictionary. If the key exists, it returns the 
        corresponding value. Otherwise, it defaults to returning 1.

        Returns:
            int: The value of the 'blink' setting if it exists, otherwise 1.
        """
        if 'blink' in self.prefs_dic[user_vars._popups_settings_].keys():
            return self.prefs_dic[user_vars._popups_settings_]['blink']
        else:
            return 1

    def get_app_scale(self):
        """
        Retrieves the application scale preference from the user's preferences dictionary.

        Returns:
            str: The application scale value if it exists in the preferences dictionary,
                 otherwise returns the default value "0.9".
        """
        if user_vars._app_scale_ in self.prefs_dic.keys():
            return self.prefs_dic[user_vars._app_scale_]
        else:
            return "0.9"

    def set_app_scale(self, app_scale):
        """
        Updates the application scale preference for the user and saves the updated preferences.

        Args:
            app_scale (float): The new application scale value to be set.

        Returns:
            int: Always returns 1 to indicate the operation was successful.
        """
        self.prefs_dic[user_vars._app_scale_] = app_scale
        self.write_prefs_dic()
        return 1

    def get_keep_until_comment(self):
        """
        Retrieves the user's preference for keeping popups visible until a comment is made.

        This method accesses the `keep_until_comment` setting from the user's popup settings
        in the preferences dictionary.

        Returns:
            bool: True if popups should remain visible until a comment is made, False otherwise.
        """
        return self.prefs_dic[user_vars._popups_settings_]['keep_until_comment']

    def get_popups_duration(self):
        """
        Retrieve the duration of popups from the user's preferences.

        Returns:
            int: The duration of popups as specified in the user's preferences.
        """
        return self.prefs_dic[user_vars._popups_settings_]['duration']

    def get_local_path(self):
        """
        Retrieves the cleaned local path from the user's preferences dictionary.

        Returns:
            str: The cleaned local path as specified in the user's preferences.
        """
        return path_utils.clean_path(self.prefs_dic[user_vars._local_path_])

    def get_user_build(self):
        """
        Retrieves the user's build preference from the preferences dictionary.

        If the user's build preference key (`_user_build_`) is not found in the 
        preferences dictionary, it sets the user's build preference to `None`.

        Returns:
            The value associated with the user's build preference key in the 
            preferences dictionary.

        Raises:
            KeyError: If the `_user_build_` key is not present in the dictionary 
                      after attempting to set it to `None`.
        """
        if user_vars._user_build_ not in self.prefs_dic.keys():
            self.set_user_build(None)
        return self.prefs_dic[user_vars._user_build_]

    def set_user_build(self, build):
        """
        Updates the user's build preference and writes the updated preferences to the preferences dictionary.

        Args:
            build (str): The build identifier to set for the user.

        Side Effects:
            - Updates the `prefs_dic` dictionary with the new build value.
            - Calls `write_prefs_dic` to persist the updated preferences.
        """
        self.prefs_dic[user_vars._user_build_] = build
        self.write_prefs_dic()

    def get_user_prefs_dic(self):
        """
        Retrieves or initializes the user preferences dictionary.
        This method checks if the user preferences file exists. If it does not exist,
        it initializes a default preferences dictionary with predefined keys and values,
        creates the necessary directories, and writes the dictionary to the file. If the
        file exists, it loads the preferences dictionary from the file.
        Attributes:
            self.user_prefs_file (str): Path to the user preferences file.
            self.prefs_dic (dict): Dictionary containing user preferences.
        Behavior:
            - Creates the user preferences directory if it does not exist.
            - Initializes default preferences if the preferences file is missing.
            - Loads preferences from the file if it exists.
        Default Preferences:
            - Database connection settings, repository, team DNS, and various context settings.
            - Popup settings including enabled status, duration, and comment retention.
            - Reference settings such as auto-update behavior.
            - Splash screen visibility, user build, and widget positions.
        Raises:
            FileNotFoundError: If the preferences file cannot be found when attempting to load it.
            yaml.YAMLError: If there is an error parsing the YAML file.
        Note:
            This method uses the `yaml` library for reading and writing the preferences file.
        """
        self.user_prefs_file = user_vars._user_prefs_file_
        path_utils.mkdir(user_vars._user_path_)
        if not path_utils.isfile(self.user_prefs_file):
            self.prefs_dic = dict()
            self.prefs_dic[user_vars._psql_dns_] = None
            self.prefs_dic[user_vars._repository_] = None
            self.prefs_dic[user_vars._team_dns_] = None
            self.prefs_dic[user_vars._tree_context_] = dict()
            self.prefs_dic[user_vars._tabs_context_] = dict()
            self.prefs_dic[user_vars._versions_context_] = dict()
            self.prefs_dic[user_vars._videos_context_] = dict()
            self.prefs_dic[user_vars._wall_context_] = dict()
            self.prefs_dic[user_vars._asset_tracking_context_] = dict()
            self.prefs_dic[user_vars._console_context_] = dict()
            self.prefs_dic[user_vars._production_manager_context_] = dict()
            self.prefs_dic[user_vars._local_path_] = None
            self.prefs_dic[user_vars._popups_settings_] = dict()
            self.prefs_dic[user_vars._popups_settings_]['enabled'] = 1
            self.prefs_dic[user_vars._popups_settings_]['keep_until_comment'] = True
            self.prefs_dic[user_vars._popups_settings_]['duration'] = 3
            self.prefs_dic[user_vars._reference_settings_] = dict()
            self.prefs_dic[user_vars._reference_settings_]['auto_update_default'] = False

            self.prefs_dic[user_vars._show_splash_screen_] = True
            self.prefs_dic[user_vars._user_build_] = None
            self.prefs_dic[user_vars._widgets_pos_] = dict()
            self.write_prefs_dic()
        else:
            with open(self.user_prefs_file, 'r') as f:
                self.prefs_dic = yaml.load(f, Loader=yaml.Loader)

    def write_prefs_dic(self):
        """
        Writes the user preferences dictionary to a YAML file.

        This method serializes the `prefs_dic` attribute and writes it to the file
        specified by the `user_prefs_file` attribute.

        Raises:
            OSError: If there is an issue opening or writing to the file.
        """
        with open(self.user_prefs_file, 'w') as f:
            yaml.dump(self.prefs_dic, f)

    def execute_session(self, script):
        """
        Executes a given script within a session context.

        This function writes the provided script to a session file, analyzes the script
        for forbidden modules, and reloads the session module if the script passes the analysis.
        It handles interruptions and logs errors during execution.

        Args:
            script (str): The script content to be executed.

        Raises:
            KeyboardInterrupt: If the execution is manually interrupted.
            Exception: Logs any other exceptions that occur during execution.
        """
        with open(user_vars._session_file_, 'w') as f:
            f.write(script)
        try:
            if not analyze_module(script,
                                  forbidden_modules=['wizard.core.game'],
                                  ignore_nest=['wizard.core.assets',
                                               'wapi',
                                               'wizard.core.project']):
                logger.info("Skipping script execution")
                return
            importlib.reload(session)
        except KeyboardInterrupt:
            logger.warning("Execution manually stopped")
        except:
            logger.error(sys.exc_info()[1])

    def execute_py(self, file):
        """
        Executes a Python script from the specified file.

        Args:
            file (str): The path to the Python file to be executed.

        Returns:
            None

        Logs:
            - A warning if the specified file does not exist.

        Behavior:
            - Reads the content of the file if it exists.
            - Passes the file content to the `execute_session` method for execution.
        """
        if not path_utils.isfile(file):
            logger.warning(f"{file} doesn't exists")
            return
        with open(file, 'r') as f:
            data = f.read()
        self.execute_session(data)


def analyze_module(script, forbidden_modules, ignore_nest=[]):
    """
    Analyzes the dependencies of a given Python script to identify forbidden modules.

    This function parses the provided Python script to extract its direct and nested
    dependencies. It checks if any of the dependencies belong to a list of forbidden
    modules and returns an authorization status accordingly.

    Args:
        script (str): The Python script to analyze, provided as a string.
        forbidden_modules (list): A list of module names that are not allowed to be used.
        ignore_nest (list, optional): A list of module names to ignore when analyzing nested dependencies. Defaults to an empty list.

    Returns:
        int: Returns 1 if no forbidden modules are found, otherwise returns 0.

    Raises:
        ModuleNotFoundError: If a module cannot be imported during dependency analysis.

    Notes:
        - The function uses the `ast` module to parse the script and extract import statements.
        - It iteratively traverses dependencies to include nested imports unless specified in `ignore_nest`.
        - Logs debug information about the analyzed dependencies and errors for forbidden modules.
    """
    # Use a set to store all dependencies, including nested ones
    all_dependencies = set()
    dependencies_to_check = set()
    tree = ast.parse(script)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                all_dependencies.add(alias.name)
                dependencies_to_check.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                module_path = node.module
                for name in node.names:
                    all_dependencies.add(f"{module_path}.{name.name}")
                    dependencies_to_check.add(f"{module_path}.{name.name}")
    # Traverse the dependencies iteratively
    while dependencies_to_check:
        dependency = dependencies_to_check.pop()
        all_dependencies.add(dependency)
        # Get the module's dependencies
        try:
            module = importlib.import_module(dependency)
            if dependency in ignore_nest:
                continue
            for _, value in vars(module).items():
                if isinstance(value, type(module)):
                    dependency_name = value.__name__
                    if dependency_name not in all_dependencies:
                        dependencies_to_check.add(dependency_name)
        except ModuleNotFoundError:
            continue
    # Do something with the module and its dependencies
    logger.debug(f"Analyzing session and dependencies {all_dependencies}")
    authorized = 1
    for module_name in forbidden_modules:
        if module_name in all_dependencies:
            logger.error(
                f"You are trying to use a forbidden module : {module_name}")
            authorized = 0
    return authorized


def log_user(user_name, password):
    """
    Logs in a user by verifying their credentials and setting up their environment.

    Args:
        user_name (str): The username of the user attempting to log in.
        password (str): The password provided by the user.

    Returns:
        int or None: Returns 1 if the login is successful, otherwise None.

    Logs:
        - An error if the username does not exist in the repository.
        - A warning if the password is incorrect.
        - An info message when the user successfully signs in.

    Side Effects:
        - Updates the current IP data for the user in the repository.
        - Builds the user's environment using the provided user data.
    """
    if user_name not in repository.get_user_names_list():
        logger.error(f"{user_name} doesn't exists")
        return
    user_row = repository.get_user_row_by_name(user_name)
    if not tools.decrypt_string(user_row['pass'],
                                password):
        logger.warning(f'Wrong password for {user_name}')
        return
    repository.update_current_ip_data('user_id', user_row['id'])
    environment.build_user_env(user_row)
    logger.info(f'{user_name} signed in')
    return 1


def disconnect_user():
    """
    Disconnects the current user by updating the repository to set the 
    'user_id' field to None and logs the disconnection event.

    This function is typically used to log out a user or clear their 
    session data.
    """
    repository.update_current_ip_data('user_id', None)
    logger.info('You are now disconnected')


def get_user():
    """
    Retrieves the current user's ID from the repository and builds the user's environment
    if a valid user ID is found.

    This function performs the following steps:
    1. Fetches the current user's ID using the repository's `get_current_ip_data` method.
    2. If no user ID is found, the function returns without performing further actions.
    3. If a user ID is found, it retrieves the user's data using the repository's `get_user_data` method.
    4. Builds the user's environment using the `environment.build_user_env` method with the retrieved user data.
    5. Returns `1` to indicate successful execution.

    Returns:
        int or None: Returns `1` if the user's environment is successfully built, otherwise `None`.
    """
    user_id = repository.get_current_ip_data('user_id')
    if not user_id:
        return
    environment.build_user_env(user_row=repository.get_user_data(user_id))
    return 1


def log_project(project_name, password, wait_for_restart=False):
    """
    Logs into a project by verifying the project name and password, and sets up the environment.

    Args:
        project_name (str): The name of the project to log into.
        password (str): The password for the project.
        wait_for_restart (bool, optional): If True, skips environment setup and database modification. Defaults to False.

    Returns:
        int: Returns 1 if the login is successful.
        None: Returns None if the project does not exist or the password is incorrect.

    Logs:
        - Error if the project does not exist.
        - Warning if the password is incorrect.
        - Info if the login is successful.
    """
    if project_name not in repository.get_projects_names_list():
        logger.error(f"{project_name} doesn't exists")
        return
    project_row = repository.get_project_row_by_name(project_name)
    if not tools.decrypt_string(project_row['project_password'],
                                password):
        logger.warning(f'Wrong password for {project_name}')
        return
    repository.update_current_ip_data('project_id', project_row['id'])
    logger.info(f'Successfully signed in {project_name} project')
    if not wait_for_restart:
        environment.build_project_env(
            project_name, project_row['project_path'])
        db_utils.modify_db_name('project', project_name)
        project.add_user(repository.get_user_row_by_name(environment.get_user(),
                                                         'id'))
    return 1


def log_project_without_cred(project_name):
    """
    Logs into a project without requiring credentials.

    This function performs the following steps:
    1. Checks if the given project name exists in the repository.
       - Logs an error and exits if the project does not exist.
    2. Retrieves the project row data by the project name.
    3. Updates the current IP data with the project's ID.
    4. Builds the project environment using the project's name and path.
    5. Modifies the database name to match the project name.
    6. Logs a success message indicating the project has been signed in.
    7. Adds the current user to the project.

    Args:
        project_name (str): The name of the project to log into.

    Returns:
        int: Returns 1 on successful execution.

    Logs:
        - Error if the project does not exist.
        - Info on successful project sign-in.
    """
    if project_name not in repository.get_projects_names_list():
        logger.error(f"{project_name} doesn't exists")
        return
    project_row = repository.get_project_row_by_name(project_name)
    repository.update_current_ip_data('project_id', project_row['id'])
    environment.build_project_env(project_name, project_row['project_path'])
    db_utils.modify_db_name('project', project_name)
    logger.info(f'Successfully signed in {project_name} project')
    project.add_user(repository.get_user_row_by_name(environment.get_user(),
                                                     'id'))
    return 1


def disconnect_project():
    """
    Disconnects the current project by updating the repository to set the 
    'project_id' to None. Logs a message indicating the successful disconnection.

    This function is typically used to clear the association with the current 
    project in the system.
    """
    repository.update_current_ip_data('project_id', None)
    logger.info('Successfully disconnect from project')


def get_project():
    """
    Retrieves the current project ID and sets up the project environment.

    This function fetches the current project ID from the repository. If a valid
    project ID is found, it retrieves the corresponding project details (such as
    project name and path) and initializes the project environment using these details.

    Returns:
        int or None: Returns 1 if the project environment is successfully built,
        otherwise returns None if no project ID is found.
    """
    project_id = repository.get_current_ip_data('project_id')
    if not project_id:
        return
    project_row = repository.get_project_row(project_id)
    environment.build_project_env(project_name=project_row['project_name'],
                                  project_path=project_row['project_path'])
    return 1
