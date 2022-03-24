# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export

def main():
    export_name = 'main'
    export_GRP = 'custom_GRP'
    if wizard_tools.check_obj_list_existence([export_GRP]):
        wizard_export.export('custom', export_name, [export_GRP])

