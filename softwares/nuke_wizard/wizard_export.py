# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging

# Nuke modules
import nuke

# Wizard modules
import wizard_hooks
import wizard_communicate
from nuke_wizard import wizard_tools

logger = logging.getLogger(__name__)


def export(stage_name, export_name, exported_string_asset, frange=[0, 0], custom_work_env_id=None, comment='', prepare_only=False):
    if trigger_sanity_hook(stage_name, exported_string_asset):
        if custom_work_env_id:
            work_env_id = custom_work_env_id
        else:
            work_env_id = int(os.environ['wizard_work_env_id'])

        if wizard_communicate.get_export_format(work_env_id) == 'exr':
            export_dir = wizard_communicate.request_render(int(os.environ['wizard_version_id']),
                                                           work_env_id,
                                                           export_name,
                                                           comment=comment)
            export_exr(export_dir, frange, prepare_only)
        else:
            export_file = wizard_communicate.request_export(work_env_id,
                                                            export_name)
            export_by_extension(export_file, frange)
            export_dir = wizard_communicate.add_export_version(export_name,
                                                               [export_file],
                                                               work_env_id,
                                                               int(
                                                                   os.environ['wizard_version_id']),
                                                               comment=comment)
        trigger_after_export_hook(
            stage_name, export_dir, exported_string_asset)


def export_by_extension(export_file, frange):
    if export_file.endswith('.nk'):
        export_nk(export_file, frange)
    else:
        logger.info("{} extension is unkown".format(export_file))


def after_exr_render(frange):
    nuke.removeAfterFrameRender(wizard_tools.by_frame_progress, args=(frange))
    nuke.removeAfterRender(after_exr_render, args=(frange))


def export_exr(export_dir, frange, prepare_only=False):
    render_node_name = 'wizard_render_node'
    if render_node_name in wizard_tools.get_all_nodes_names():
        render_node = nuke.toNode(render_node_name)
        file = f"{export_dir}/%05d.exr"
        render_node['file'].setValue(file)
        render_node['first'].setValue(frange[0])
        render_node['last'].setValue(frange[1])
        render_node['use_limit'].setValue(True)
        render_node.knob('afterFrameRender')
        nuke.addAfterRender(after_exr_render, args=(frange))
        nuke.addAfterFrameRender(wizard_tools.by_frame_progress, args=(frange))
        if prepare_only:
            logger.info(f"Prepared EXR export to {export_dir}")
            return
        nuke.execute(render_node_name, frange[0], frange[1], 1)
    else:
        logger.warning(f"{render_node_name} not found")


def reopen(scene):
    nuke.scriptClear()
    nuke.scriptOpen(scene)
    logger.info("Opening file {}".format(scene))


def save_or_save_increment():
    scene = nuke.root()['name'].value()
    if scene == '':
        wizard_tools.save_increment()
        scene = nuke.root()['name'].value()
    else:
        nuke.scriptSave()
        if os.environ["wizard_launch_mode"] == 'gui':
            wizard_communicate.screen_over_version(
                int(os.environ['wizard_version_id']))
        logger.info("Saving file {}".format(scene))
    return scene


def export_nk(export_file, frange):
    logger.info("Exporting .nk")
    nuke.scriptSaveAs(export_file)


def trigger_sanity_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.sanity_hooks('nuke', stage_name, string_asset, exported_string_asset)


def trigger_before_export_hook(stage_name, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.before_export_hooks(
        'nuke', stage_name, string_asset, exported_string_asset)
    logger.warning(
        "Ignoring additionnal objects from before export hooks. ( Wizard/Nuke exception )")


def trigger_after_export_hook(stage_name, export_dir, exported_string_asset):
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    wizard_hooks.after_export_hooks(
        'nuke', stage_name, export_dir, string_asset, exported_string_asset)
