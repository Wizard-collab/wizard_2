# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
import os
import logging

# Wizard modules
import wizard_communicate
import wizard_hooks
from substance_designer_wizard import wizard_tools

# Substance designer modules
import sd

logger = logging.getLogger(__name__)
ctx = sd.getContext()
logger.addHandler(ctx.createRuntimeLogHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

def save_or_save_increment():
    return wizard_tools.save_or_save_increment()

def reopen(file):
    pkgMgr = wizard_tools.get_packageMgr()
    pkgMgr.loadUserPackage(sdPackageFileAbsPath=file,
                            updatePackages = True,
                            reloadIfModified = True)

def export(stage_name, export_name, exported_string_asset, comment=''):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        work_env_id = int(os.environ['wizard_work_env_id'])
        export_file = wizard_communicate.request_export(work_env_id,
                                                                export_name)
        export_files_list = export_by_extension(export_file)
        export_dir = wizard_communicate.add_export_version(export_name,
                                                export_files_list,
                                                work_env_id,
                                                int(os.environ['wizard_version_id']),
                                                comment=comment)
        trigger_after_export_hook(stage_name, export_dir, exported_string_asset)

def export_by_extension(export_file):
    if export_file.endswith('.sbsar'):
        return export_sbsar(export_file)

def export_sbsar(export_file):
    exporterInstance = wizard_tools.get_SDSBSARExporter()
    exporter = exporterInstance.sNew()
    pkg = wizard_tools.get_wizard_pkg()
    exporter.exportPackageToSBSAR(pkg, export_file)
    return [export_file]

def trigger_sanity_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    return wizard_hooks.sanity_hooks('substance_designer', stage_name, string_asset, exported_string_asset)

def trigger_before_export_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.before_export_hooks('substance_designer', stage_name, string_asset, exported_string_asset)
    return None

def trigger_after_export_hook(stage_name, export_dir, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks('substance_designer', stage_name, export_dir, string_asset, exported_string_asset)
