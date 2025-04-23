# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging

# Wizard modules
import wizard_communicate
from maya_wizard import wizard_tools
from maya_wizard import wizard_export

# Maya modules
import pymel.core as pm

logger = logging.getLogger(__name__)


def main(comment=''):
    scene = wizard_export.save_or_save_increment()
    try:
        groups_dic = wizard_tools.get_export_grps('rigging_GRP')
        if groups_dic == dict():
            logger.warning("No group to export...")
            return
        for grp_name in groups_dic.keys():
            logger.info(f"Exporting {grp_name}...")
            export_name = groups_dic[grp_name]
            if export_name != 'main':
                render_set = f'render_set_{export_name}'
            else:
                render_set = 'render_set'
            if wizard_tools.check_obj_list_existence([render_set]):
                rigging_GRP_node = pm.PyNode(grp_name)
                render_set_node = pm.PyNode(render_set)
                asset_name = os.environ['wizard_asset_name']
                rigging_GRP_node.rename(asset_name)
                main_render_set_obj = wizard_tools.rename_render_set(
                    render_set_node)
                export_GRP_list = [asset_name, 'render_set']
                exported_string_asset = wizard_communicate.get_string_variant_from_work_env_id(
                    os.environ['wizard_work_env_id'])
                additionnal_objects = wizard_export.trigger_before_export_hook(
                    'rigging', exported_string_asset)
                export_GRP_list += additionnal_objects
                wizard_export.export(
                    'rigging', export_name, exported_string_asset, export_GRP_list, comment=comment)
                rigging_GRP_node.rename(grp_name)
                render_set_node.rename(render_set)
                if main_render_set_obj is not None:
                    main_render_set_obj.rename('render_set')
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        wizard_export.reopen(scene)
