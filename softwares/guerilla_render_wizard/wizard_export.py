# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Guerilla modules
import guerilla
from guerilla import Document, pynode

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_tools

def export(stage_name):
    if stage_name == 'shading':
        export_dir = export_shading()
    if stage_name == 'custom':
        export_dir = export_custom()

def export_shading():
    export_name = 'main'
    export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
    if export_from_extension(export_file, 'shading_GRP'):
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_version_id']))

def export_custom():
    export_name = 'main'
    export_file = wizard_communicate.request_export(int(os.environ['wizard_work_env_id']),
                                                                export_name)
    if export_from_extension(export_file, 'custom_GRP'):
        export_dir = wizard_communicate.add_export_version(export_name,
                                                            [export_file],
                                                            int(os.environ['wizard_version_id']))

def export_from_extension(file, export_GRP):
    extension = file.split('.')[-1]
    if extension == 'gnode':
        return export_node(file, export_GRP)
    elif extension == 'gproject':
        return export_project(file, export_GRP)

def export_node(file, export_GRP):
    if export_GRP in wizard_tools.get_all_nodes():
        grp_node = wizard_tools.get_node_from_name(export_GRP)
        grp_node.savefile(file)
        return 1
    else:
        logger.warning('{0} not found'.format(export_GRP))
        return None

def export_project(file, export_GRP):
    if export_GRP in wizard_tools.get_all_nodes():
        filename = Document().getfilename()
        Document().save(file)
        Document().load(filename)
        return 1
    else:
        logger.warning('{0} not found'.format(export_GRP))
        return None


