# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from maya_wizard import wizard_tools

# Maya modules
import pymel.core as pm

def main():
    export_name = 'main'
    if wizard_tools.check_obj_list_existence(['rigging_GRP', 'render_set']):
        export_GRP_list = ['rigging_GRP', 'render_set']
        wizard_export.export('rigging', export_name, export_GRP_list)
