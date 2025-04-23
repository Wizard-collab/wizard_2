# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Maya modules
import maya.cmds as cmds
import pymel.core as pm

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools

logger = logging.getLogger(__name__)


def main(comment=''):
    groups_dic = wizard_tools.get_export_grps('grooming_GRP')
    if groups_dic == dict():
        logger.warning("No group to export...")
        return

    for grp_name in groups_dic.keys():
        logger.info(f"Exporting {grp_name}...")
        grp_obj = pm.PyNode(grp_name)
        object_list = pm.listRelatives(grp_obj,
                                       allDescendents=True)
        work_env_id = int(os.environ['wizard_work_env_id'])
        export_name = groups_dic[grp_name]
        for node in object_list:
            relatives = pm.listRelatives(node, shapes=True)
            if len(relatives) != 1:
                continue
            if pm.nodeType(relatives[0]) != 'xgmSplineDescription':
                continue
            fur_export_name = f"{export_name}_{node.getName().split(':')[-1]}"
            export_dir = wizard_communicate.add_export_version(fur_export_name,
                                                               [],
                                                               work_env_id,
                                                               int(os.environ['wizard_version_id']))
            file_path = os.path.join(
                export_dir, f'xgen_grooming__{fur_export_name}.abc')
            print(node.getName())
            command = f"-obj {node.getName()} "
            command += f"-file {file_path} "
            command += f"-df 'ogawa' "
            command += f"-fr 0 1 "
            command += "-step 1 -wfw"
            cmds.xgmSplineCache(export=True, j=command)
