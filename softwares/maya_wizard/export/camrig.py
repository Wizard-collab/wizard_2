# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Wizard modules
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

def main():
    export_name = 'main'
    if wizard_tools.check_obj_list_existence(['camrig_GRP', 'render_set']):
        rigging_GRP_node = pm.PyNode('camrig_GRP')
        asset_name = os.environ['wizard_asset_name']
        rigging_GRP_node.rename(asset_name)
        export_GRP_list = [asset_name, 'render_set']

        additionnal_objects = wizard_export.trigger_before_export_hook('camrig')
        export_GRP_list += additionnal_objects

        wizard_export.export('camrig', export_name, export_GRP_list)
