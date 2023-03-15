import maya.cmds as cmds
import pymel.core as pm
import wizard_communicate
import os

export_name = 'xgen'
work_env_id = int(os.environ['wizard_work_env_id'])
export_dir = wizard_communicate.add_export_version(export_name,
                                        [],
                                        work_env_id,
                                        int(os.environ['wizard_version_id']))
for node in pm.ls():
    relatives = pm.listRelatives(node, shapes=True)
    if len(relatives) != 1:
        continue
    if pm.nodeType(relatives[0]) != 'xgmSplineDescription':
        continue
    file_path = os.path.join(export_dir, f'xgen_cache__{node.getName()}.abc')
    frame_range = wizard_communicate.get_frame_range(int(os.environ['wizard_work_env_id']))
    command = f"-obj {node.getName()} "
    command += f"-file {file_path} "
    command += f"-df 'ogawa' "
    command += f"-fr {frame_range[1]} {frame_range[2]} "
    command += "-step 1 -mxf -wfw"
    cmds.xgmSplineCache(export=True, j=command)