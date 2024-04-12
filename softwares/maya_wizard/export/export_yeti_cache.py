# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import json
import traceback
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools
from maya_wizard import wizard_export
from maya_wizard.export import cfx

# Maya modules
import pymel.core as pm
import maya.cmds as cmds

def invoke_settings_widget(*args):
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('cfx', parent=wizard_tools.maya_main_window())
    if export_settings_widget_win.exec_() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def main(nspace_list, frange):
    for nspace in nspace_list:
        work_env_id = int(os.environ['wizard_work_env_id'])

        for node in pm.ls():
            relatives = pm.listRelatives(node, shapes=True)
            if len(relatives) != 1:
                continue
            if pm.nodeType(relatives[0]) != 'pgYetiMaya':
                continue
            if nspace not in str(node):
                continue

            yeti_node = pm.listRelatives(node, shapes=True)[0]

            fur_export_name = f"{nspace}_{node.getName().split(':')[-1]}"
            export_dir = wizard_communicate.add_export_version(fur_export_name,
                                                    [],
                                                    work_env_id,
                                                    int(os.environ['wizard_version_id']))

            logger.info("Exporting .fur")
            node_name = node.split(':')[-1]
            file = os.path.join(export_dir, 'yeti_cache__{}.%04d.fur'.format(node_name))
            pm.select(yeti_node, r=True)
            cmds.pgYetiCommand(writeCache=file, range=(frange[0], frange[1]), samples=3, sampleTimes= "-0.2 0.0 0.2")
