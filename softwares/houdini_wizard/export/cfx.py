# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
import wizard_communicate
from houdini_wizard import wizard_tools
from houdini_wizard import wizard_export

def main(nspace_list, frange, comment='', prepare_only=False):
    scene = wizard_export.save_or_save_increment()
    try:
        at_least_one = False
        rigging_references = get_rig_nspaces()
        if rigging_references:
            for rigging_reference in rigging_references:
                if rigging_reference['namespace'] in nspace_list:
                    at_least_one = True
                    export_cfx(rigging_reference, frange, comment=comment, prepare_only=prepare_only)
            if not at_least_one:
                logger.warning(f"Nothing to export from namespace list : {nspace_list}")
        else:
            logger.warning("No rigging or grooming references found in wizard description")
    except:
        logger.error(str(traceback.format_exc()))
    finally:
        pass
        #wizard_export.reopen(scene)

def invoke_settings_widget(prepare_only=False):
    from wizard_widgets import export_settings_widget
    export_settings_widget_win = export_settings_widget.export_settings_widget('cfx')
    if export_settings_widget_win.exec() == export_settings_widget.dialog_accepted:
        nspace_list = export_settings_widget_win.nspace_list
        frange = export_settings_widget_win.frange
        main(nspace_list, frange, prepare_only=prepare_only)

def export_cfx(rigging_reference, frange, comment='', prepare_only=False):
    rig_nspace = rigging_reference['namespace']
    asset_name = rigging_reference['asset_name']
    variant_name = rigging_reference['variant_name']
    exported_string_asset = rigging_reference['string_stage']
    count = rigging_reference['count']

    out_nodes_dic = wizard_tools.get_export_nodes('wizard_cfx_output', parent=wizard_tools.look_for_node(rig_nspace))
    if out_nodes_dic == dict():
        logger.warning("No export nodes found...")
        return
    for out_node_name in out_nodes_dic.keys():
        logger.info(f"Exporting {rig_nspace} | {out_node_name}")
        wizard_export.trigger_before_export_hook('cfx', exported_string_asset)
        export_name = buid_export_name(asset_name, variant_name, count, out_nodes_dic[out_node_name])
        wizard_export.export(stage_name='cfx', export_name=export_name, out_node=out_node_name, exported_string_asset=exported_string_asset, frange=frange, parent=rig_nspace, comment=comment, prepare_only=prepare_only)

def buid_export_name(asset_name, variant_name, count, additionnal_name):
    if variant_name == 'main':
        export_name = asset_name
    else:
        export_name = "{}_{}".format(asset_name, variant_name)
    if count != '0':
        export_name += "_{}".format(count)
    if additionnal_name != 'main':
        export_name += "_{}".format(additionnal_name)
    return export_name

def get_rig_nspaces():
    references = wizard_communicate.get_references(int(os.environ['wizard_work_env_id']))
    to_return = []
    if 'rigging' not in references.keys() and 'grooming' not in references.keys():
        logger.warning("No rigging or grooming references found")
        return
    if 'rigging' in references.keys():
        to_return += references['rigging']
    if 'grooming' in references.keys():
        to_return += references['grooming']
    return to_return
