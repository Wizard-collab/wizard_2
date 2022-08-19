# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
import os
import traceback
import logging

logger = logging.getLogger(__name__)

if sys.version_info[0] < 3:
	import imp
else:
	import importlib

# Wizard modules
import wizard_communicate

hooks = dict()
hooks['blender'] = 'blender_hook.py'
hooks['guerilla_render'] = 'guerilla_render_hook.py'
hooks['maya'] = 'maya_hook.py'
hooks['houdini'] = 'houdini_hook.py'
hooks['nuke'] = 'nuke_hook.py'
hooks['substance_painter'] = 'substance_painter_hook.py'
hooks['substance_designer'] = 'substance_designer_hook.py'

def after_save_hooks(software, stage_name, string_asset, scene_path):
	sanity = True
	hooks_modules = get_hooks_modules(software)
	for module_name in hooks_modules.keys():
		try:
			logger.info("Executing {0} after save hook from {1}".format(module_name,
																hooks_modules[module_name]['path']))
			hooks_modules[module_name]['module'].after_save(stage_name, string_asset, scene_path)
		except:
			logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
																hooks_modules[module_name]['path']))
			logger.error(traceback.format_exc())
	return sanity

def sanity_hooks(software, stage_name, string_asset, exported_string_asset):
	sanity = True
	hooks_modules = get_hooks_modules(software)
	for module_name in hooks_modules.keys():
		try:
			logger.info("Executing {0} sanity hook from {1}".format(module_name,
																hooks_modules[module_name]['path']))
			module_sanity = hooks_modules[module_name]['module'].sanity(stage_name, string_asset, exported_string_asset)
			if not module_sanity:
				logger.info("{0} sanity not passed. Skipping export".format(module_name))
				sanity *= module_sanity
		except:
			logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
																hooks_modules[module_name]['path']))
			logger.error(traceback.format_exc())
	return sanity

def before_export_hooks(software, stage_name, string_asset, exported_string_asset):
	additionnal_objects = []
	hooks_modules = get_hooks_modules(software)
	for module_name in hooks_modules.keys():
		try:
			logger.info("Executing {0} before export hook from {1}".format(module_name,
																hooks_modules[module_name]['path']))
			nodes = hooks_modules[module_name]['module'].before_export(stage_name, string_asset, exported_string_asset)
			if type(nodes) != list:
				logger.error("Before export hook {0} return {1} instead of list. Skipping.".format(module_name, type(nodes)))
			else:
				if len(nodes) > 0:
					logger.info("Adding the following objects from {0}:".format(module_name))
					for node in nodes:
						logger.info("    {0}".format(node))
					additionnal_objects += nodes
		except:
			logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
																hooks_modules[module_name]['path']))
			logger.error(traceback.format_exc())
	return list(set(additionnal_objects))

def after_export_hooks(software, stage_name, export_dir, string_asset, exported_string_asset):
	hooks_modules = get_hooks_modules(software)
	for module_name in hooks_modules.keys():
		try:
			logger.info("Executing {0} after export hook from {1}".format(module_name,
																hooks_modules[module_name]['path']))
			hooks_modules[module_name]['module'].after_export(stage_name, export_dir, string_asset, exported_string_asset)
		except:
			logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
																hooks_modules[module_name]['path']))
			logger.error(traceback.format_exc())

def after_reference_hooks(software,
	                        stage_name,
	                        referenced_stage_name,
	                        referenced_files_dir,
	                        namespace,
	                        new_objects,
	                        string_asset,
	                        referenced_string_asset):
	hooks_modules = get_hooks_modules(software)
	for module_name in hooks_modules.keys():
		try:
			logger.info("Executing {0} after reference hook from {1}".format(module_name,
																hooks_modules[module_name]['path']))
			hooks_modules[module_name]['module'].after_reference(stage_name,
										                        referenced_stage_name,
										                        referenced_files_dir,
										                        namespace,
										                        new_objects,
										                        string_asset,
										                        referenced_string_asset)
		except:
			logger.error("Can't execute module {0} from {1}, skipping".format(module_name,
																hooks_modules[module_name]['path']))
			logger.error(traceback.format_exc())


def get_hooks_modules(software):
	hooks_modules = dict()
	# Load user hooks
	plugins_path = wizard_communicate.get_plugins_folder()
	hooks_path = wizard_communicate.get_hooks_folder()
	# Load defaults hooks
	module_name, module_path = load_module(software, hooks_path, hook_type='default_hook')
	if module_name and module_path:
		hooks_modules[module_name] = dict()
		hooks_modules[module_name]['module'] = sys.modules[module_name]
		hooks_modules[module_name]['path'] = module_path

	module_name = None
	module_path = None

	# Load plugins hooks
	if os.path.isdir(plugins_path):
		for folder in os.listdir(plugins_path):
			plugin_path = os.path.join(plugins_path, folder)
			module_name, module_path = load_module(software, plugin_path, hook_type="plugin_{0}".format(folder))
			if module_name and module_path:
				hooks_modules[module_name] = dict()
				hooks_modules[module_name]['module'] = sys.modules[module_name]
				hooks_modules[module_name]['path'] = module_path
				module_name = None
				module_path = None

	return hooks_modules

def load_module(software, plugin_path, hook_type):
	module_name = '{0}_{1}'.format(hook_type, software)
	module_path = os.path.join(plugin_path, hooks[software])
	try:
		if not os.path.isfile(module_path):
			logger.info("Hook {0} not found, skipping".format(module_path))
			return None, None
		else:
			if sys.version_info[0] < 3:
				imp.load_source(module_name, module_path)
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
