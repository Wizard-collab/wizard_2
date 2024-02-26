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

# Python modules
import os
import sys
import logging
import importlib
import traceback

# Wizard modules
from wizard.core import project
from wizard.core import environment
from wizard.core import path_utils
from wizard.vars import project_vars

logger = logging.getLogger(__name__)

def init_wizard_hooks():
    hook_path = project.get_hooks_folder()
    plugin_path = project.get_plugins_folder()
    scripts_path = project.get_scripts_folder()
    sys.path.append(hook_path)
    sys.path.append(plugin_path)
    sys.path.append(scripts_path)

def get_hooks_modules():
    hooks_modules = dict()
    # Load user hooks
    plugins_path = project.get_plugins_folder()
    hooks_path = project.get_hooks_folder()
    # Load defaults hooks
    module_name, module_path = load_module(hooks_path, hook_type='default_hook')
    if module_name and module_path:
        hooks_modules[module_name] = dict()
        hooks_modules[module_name]['module'] = sys.modules[module_name]
        hooks_modules[module_name]['path'] = module_path

    module_name = None
    module_path = None

    # Load plugins hooks
    if os.path.isdir(plugins_path):
        for folder in os.listdir(plugins_path):
            if "pycache" in folder:
                continue
            if ".idea" in folder:
                continue
            plugin_path = os.path.join(plugins_path, folder)
            module_name, module_path = load_module(plugin_path, hook_type="plugin_{0}".format(folder))
            if module_name and module_path:
                hooks_modules[module_name] = dict()
                hooks_modules[module_name]['module'] = sys.modules[module_name]
                hooks_modules[module_name]['path'] = module_path
                module_name = None
                module_path = None

    return hooks_modules

def load_module(plugin_path, hook_type):
    module_name = '{0}_wizard'.format(hook_type)
    module_path = os.path.join(plugin_path, 'wizard_hook.py')
    try:
        if not os.path.isfile(module_path):
            logger.info("Hook {0} not found, skipping".format(module_path))
            return None, None
        else:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module 
            spec.loader.exec_module(module)
            return module_name, module_path
    except:
        logger.info("Can't load module {0}, skipping".format(module_name))
        logger.error(traceback.format_exc())
        return None, None

def after_export_hook(export_version_string, export_dir, stage_name):
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
