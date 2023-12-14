import maya.cmds as cmds
import pymel.core as pm
import wizard_communicate
import os
from wizard_widgets import export_settings_widget
from maya_wizard import wizard_tools
from PySide2 import QtWidgets

def export_xgen_dynamic_collections(*args):
    invoke_settings_widget()

def invoke_settings_widget():
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('cfx', parent=wizard_tools.maya_main_window())
    if export_settings_widget_win.exec_() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange)

def main(nspace_list, frange, comment=''):
    for nspace in nspace_list:
        work_env_id = int(os.environ['wizard_work_env_id'])

        for node in pm.ls():
            relatives = pm.listRelatives(node, shapes=True)
            if len(relatives) != 1:
                continue
            if pm.nodeType(relatives[0]) != 'xgmSplineDescription':
                continue
            if nspace not in str(node):
                continue

            fur_export_name = f"{nspace}_{node.getName().split(':')[-1]}"
            export_dir = wizard_communicate.add_export_version(fur_export_name,
                                                [],
                                                work_env_id,
                                                int(os.environ['wizard_version_id']))
            file_path = os.path.join(export_dir, f'xgen_cache__{fur_export_name}.abc')
            command = f"-obj {node.getName()} "
            command += f"-file {file_path} "
            command += f"-df 'ogawa' "
            command += f"-fr {frange[0]} {frange[1]} "
            command += f"-frs -0.2 -frs 0.2 "
            command += "-step 1 -wfw"
            cmds.xgmSplineCache(export=True, j=command)