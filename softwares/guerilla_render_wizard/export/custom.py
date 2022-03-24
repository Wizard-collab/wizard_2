# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Wizard modules
from guerilla_render_wizard import wizard_tools

def main():
    export_dic = dict()

    export_GRP = 'custom_GRP'
    if wizard_tools.check_obj_list_existence([export_GRP]):
	    export_name = 'main'
	    export_dic[export_name] = dict()
	    export_dic[export_name]['stage_name'] = 'custom'
	    export_dic[export_name]['export_GRP_list'] = [export_GRP]

    return export_dic