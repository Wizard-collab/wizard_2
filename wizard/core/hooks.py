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
This module provides functionality for managing and executing hooks in the Wizard framework.

Hooks are dynamically loaded Python modules that allow for custom behavior to be executed
at various points in the workflow. The module includes functions for initializing hooks,
loading hook modules, and executing specific hooks for events such as export, category creation,
asset creation, and more.

Key Features:
- Dynamically loads hooks from specified directories (hooks, plugins, scripts).
- Provides utility functions to execute hooks for specific events.
- Handles errors gracefully, logging any issues encountered during hook execution.

Functions:
- init_wizard_hooks: Initializes the system paths for hooks, plugins, and scripts.
- get_hooks_modules: Loads and returns a dictionary of hook modules.
- load_module: Dynamically loads a Python module from a specified file path.
- after_export_hook: Executes the `after_export` hook for all registered modules.
- after_category_creation_hook: Executes the `after_category_creation` hook for all registered modules.
- after_asset_creation_hook: Executes the `after_asset_creation` hook for all registered modules.
- after_stage_creation_hook: Executes the `after_stage_creation` hook for all registered modules.
- after_variant_creation_hook: Executes the `after_variant_creation` hook for all registered modules.
- after_work_environment_creation_hook: Executes the `after_work_environment_creation` hook for all registered modules.
- after_work_version_creation_hook: Executes the `after_work_version_creation` hook for all registered modules.
- after_reference_hook: Executes the `after_reference_creation` hook for all registered modules.

Dependencies:
- Python standard libraries: os, sys, logging, importlib, traceback.
- Wizard core modules: project, environment.

Logging:
- Uses the `logging` module to log informational and error messages.
"""

# Python modules
import os
import sys
import logging
import importlib
import traceback

# Wizard modules
from wizard.core import project
from wizard.core import environment

logger = logging.getLogger(__name__)


def init_wizard_hooks():
    """
    Initialize the Wizard hooks by appending the necessary paths
    to the system path. This allows the hooks, plugins, and scripts
    to be dynamically loaded during runtime.

    The function appends:
    - The hooks folder path
    - The plugins folder path
    - The scripts folder path
    """
    hook_path = project.get_hooks_folder()
    plugin_path = project.get_plugins_folder()
    scripts_path = project.get_scripts_folder()
    sys.path.append(hook_path)
    sys.path.append(plugin_path)
    sys.path.append(scripts_path)


def get_hooks_modules():
    """
    Loads and returns a dictionary of hook modules from the project's hooks folder 
    and plugins folder. The function distinguishes between default hooks and plugin 
    hooks, loading them dynamically.
    Returns:
        dict: A dictionary where the keys are module names and the values are dictionaries 
        containing:
            - 'module': The loaded module object.
            - 'path': The file path to the module.
    Notes:
        - Default hooks are loaded from the project's hooks folder.
        - Plugin hooks are loaded from subdirectories in the project's plugins folder.
        - Folders such as "__pycache__" and ".idea" are ignored during plugin hooks loading.
    """
    hooks_modules = dict()  # Initialize an empty dictionary to store hook modules

    # Load user hooks
    # Get the path to the plugins folder
    plugins_path = project.get_plugins_folder()
    hooks_path = project.get_hooks_folder()  # Get the path to the hooks folder

    # Load default hooks
    module_name, module_path = load_module(
        hooks_path, hook_type='default_hook')  # Load the default hook module
    if module_name and module_path:  # If the module is successfully loaded
        # Create an entry for the module in the dictionary
        hooks_modules[module_name] = dict()
        # Store the module object
        hooks_modules[module_name]['module'] = sys.modules[module_name]
        # Store the module's file path
        hooks_modules[module_name]['path'] = module_path

    module_name = None  # Reset module_name for reuse
    module_path = None  # Reset module_path for reuse

    # Load plugin hooks
    if os.path.isdir(plugins_path):  # Check if the plugins folder exists
        # Iterate through each folder in the plugins directory
        for folder in os.listdir(plugins_path):
            if "pycache" in folder:  # Skip "__pycache__" folders
                continue
            if ".idea" in folder:  # Skip ".idea" folders
                continue
            # Construct the full path to the plugin folder
            plugin_path = os.path.join(plugins_path, folder)
            module_name, module_path = load_module(
                # Load the plugin hook module
                plugin_path, hook_type="plugin_{0}".format(folder))
            if module_name and module_path:  # If the module is successfully loaded
                # Create an entry for the module in the dictionary
                hooks_modules[module_name] = dict()
                # Store the module object
                hooks_modules[module_name]['module'] = sys.modules[module_name]
                # Store the module's file path
                hooks_modules[module_name]['path'] = module_path
                module_name = None  # Reset module_name for reuse
                module_path = None  # Reset module_path for reuse

    return hooks_modules  # Return the dictionary of loaded hook modules


def load_module(plugin_path, hook_type):
    """
    Loads a Python module dynamically from a specified file path.

    Args:
        plugin_path (str): The directory path where the plugin is located.
        hook_type (str): The type of hook, used to construct the module name.

    Returns:
        tuple: A tuple containing:
            - module_name (str or None): The name of the loaded module, or None if loading failed.
            - module_path (str or None): The path to the module file, or None if loading failed.

    Logs:
        - Logs an informational message if the hook file is not found.
        - Logs an error message with a traceback if the module fails to load.

    Notes:
        - The module file is expected to be named 'wizard_hook.py' within the specified plugin path.
        - The module is added to `sys.modules` after being loaded.
    """
    module_name = '{0}_wizard'.format(hook_type)
    module_path = os.path.join(plugin_path, 'wizard_hook.py')
    try:
        if not os.path.isfile(module_path):
            logger.info("Hook {0} not found, skipping".format(module_path))
            return None, None
        else:
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            return module_name, module_path
    except:
        logger.info("Can't load module {0}, skipping".format(module_name))
        logger.error(traceback.format_exc())
        return None, None


def after_export_hook(export_version_string, export_dir, stage_name):
    """
    Executes the `after_export` hook for all registered hook modules.

    This function retrieves all hook modules, checks if the environment is in GUI mode,
    and iterates through each module to execute its `after_export` method. If an error
    occurs during the execution of a module's hook, it logs the error and continues with
    the next module.

    Args:
        export_version_string (str): The version string of the export.
        export_dir (str): The directory where the export is located.
        stage_name (str): The name of the current stage in the export process.

    Logs:
        - Info: Logs the execution of the `after_export` hook for each module.
        - Error: Logs any errors encountered while executing a module's hook, along with
          the traceback.

    Note:
        The `after_export` method of each module is expected to accept the following
        arguments: `export_version_string`, `export_dir`, `stage_name`, and `gui`.
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after export hook from {1}".format(module_name,
                                                                          hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_export(export_version_string,
                                                              export_dir,
                                                              stage_name,
                                                              gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_category_creation_hook(string_category, category_name):
    """
    Executes the `after_category_creation` hook for all registered hook modules.

    This function is called after a category is created. It iterates through all
    registered hook modules and attempts to execute their `after_category_creation`
    method, passing the provided category details and GUI environment status.

    Args:
        string_category (str): The string representation of the category.
        category_name (str): The name of the category.

    Logs:
        - Logs an info message before executing each module's hook.
        - Logs an error message if a module's hook fails to execute, along with the traceback.

    Note:
        The function skips any module whose `after_category_creation` method raises an exception.
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after category creation hook from {1}".format(module_name,
                                                                                     hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_category_creation(string_category,
                                                                         category_name,
                                                                         gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_asset_creation_hook(string_asset, asset_name):
    """
    Executes the `after_asset_creation` hook for all registered hook modules.

    This function retrieves all hook modules, checks if the environment is in GUI mode,
    and attempts to execute the `after_asset_creation` method for each module. If an
    exception occurs during the execution of a module's hook, it logs the error and
    continues with the next module.

    Args:
        string_asset (str): The string representation of the asset being created.
        asset_name (str): The name of the asset being created.

    Logs:
        - Info: Logs the execution of each module's `after_asset_creation` hook.
        - Error: Logs any errors encountered while executing a module's hook, along with
          the traceback.
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after asset creation hook from {1}".format(module_name,
                                                                                  hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_asset_creation(string_asset,
                                                                      asset_name,
                                                                      gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_stage_creation_hook(string_stage, stage_name):
    """
    Executes the `after_stage_creation` hook for all registered hook modules.

    This function retrieves all hook modules, checks if the environment is in GUI mode,
    and attempts to execute the `after_stage_creation` method for each module. If an
    exception occurs during the execution of a module's hook, it logs the error and
    continues with the next module.

    Args:
        string_stage (str): The string representation of the stage being created.
        stage_name (str): The name of the stage being created.

    Logs:
        - Info: Logs the execution of the `after_stage_creation` hook for each module.
        - Error: Logs any errors encountered while executing a module's hook.
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after stage creation hook from {1}".format(module_name,
                                                                                  hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_stage_creation(string_stage,
                                                                      stage_name,
                                                                      gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_variant_creation_hook(string_variant, variant_name):
    """
    Executes the "after variant creation" hook for all registered hook modules.

    This function iterates through all hook modules retrieved from `get_hooks_modules()`
    and attempts to execute their `after_variant_creation` method, passing the provided
    `string_variant`, `variant_name`, and a flag indicating whether the environment is GUI-based.

    Args:
        string_variant (str): The string representation of the variant being created.
        variant_name (str): The name of the variant being created.

    Logs:
        - Logs an informational message before executing each module's hook.
        - Logs an error message if a module's hook fails to execute, along with the traceback.

    Note:
        If an exception occurs while executing a module's hook, it is caught and logged,
        and the function proceeds to the next module without halting execution.
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after variant creation hook from {1}".format(module_name,
                                                                                    hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_variant_creation(string_variant,
                                                                        variant_name,
                                                                        gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_work_environment_creation_hook(string_work_env, software_name):
    """
    Executes the "after work environment creation" hook for all registered hook modules.

    This function retrieves all hook modules, checks if the environment is GUI-based, 
    and executes the `after_work_environment_creation` method for each module. 
    If an error occurs during the execution of a module's hook, it logs the error 
    and continues with the next module.

    Args:
        string_work_env (str): The name or identifier of the work environment that was created.
        software_name (str): The name of the software associated with the work environment.

    Logs:
        - Info: Logs the execution of each module's hook.
        - Error: Logs any errors encountered during the execution of a module's hook.
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after work environment creation hook from {1}".format(module_name,
                                                                                             hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_work_environment_creation(string_work_env,
                                                                                 software_name,
                                                                                 gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_work_version_creation_hook(string_work_version, version_name, file_name):
    """
    Executes the "after work version creation" hook for all registered hook modules.

    This function iterates through all hook modules retrieved from `get_hooks_modules()`
    and attempts to execute their `after_work_version_creation` method, passing the
    provided parameters. If an exception occurs during the execution of a module's hook,
    it logs the error and continues with the next module.

    Args:
        string_work_version (str): The string representation of the work version.
        version_name (str): The name of the version being created.
        file_name (str): The name of the file associated with the version.

    Returns:
        None
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after work version creation hook from {1}".format(module_name,
                                                                                         hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_work_version_creation(string_work_version,
                                                                             version_name,
                                                                             file_name,
                                                                             gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())


def after_reference_hook(string_work_environment, string_referenced_export_version, stage_name, referenced_stage_name):
    """
    Executes the "after reference creation" hook for all registered hook modules.

    This function iterates through all hook modules retrieved from `get_hooks_modules()`
    and attempts to execute their `after_reference_creation` method. It logs the execution
    status for each module and handles any exceptions that occur during execution.

    Args:
        string_work_environment (str): The working environment as a string.
        string_referenced_export_version (str): The version of the referenced export as a string.
        stage_name (str): The name of the current stage.
        referenced_stage_name (str): The name of the referenced stage.

    Returns:
        None
    """
    hooks_modules = get_hooks_modules()
    gui = environment.is_gui()
    for module_name in hooks_modules.keys():
        try:
            logger.info("Executing {0} after reference creation hook from {1}".format(module_name,
                                                                                      hooks_modules[module_name]['path']))
            hooks_modules[module_name]['module'].after_reference_creation(string_work_environment,
                                                                          string_referenced_export_version,
                                                                          stage_name,
                                                                          referenced_stage_name,
                                                                          gui)
        except:
            logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
                                                                              hooks_modules[module_name]['path']))
            logger.error(traceback.format_exc())
