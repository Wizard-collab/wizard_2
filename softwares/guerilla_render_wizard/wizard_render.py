# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Guerilla modules
import guerilla
from guerilla import Document, pynode, Modifier, RenderPass, LayerOut

# Wizard modules
import wizard_communicate
from guerilla_render_wizard import wizard_tools

logger = logging.getLogger(__name__)


def __init__():
    pass


def setup_render_directory(stage_name, export_name) -> str:
    if os.environ['wizard_stage_name'] == 'rendering':
        rendering_work_env_id = int(os.environ['wizard_work_env_id'])
    else:
        rendering_work_env_id = wizard_communicate.create_or_get_rendering_work_env(
            int(os.environ['wizard_work_env_id']))
    render_directory = wizard_communicate.request_render(int(os.environ['wizard_version_id']),
                                                         rendering_work_env_id,
                                                         export_name)
    if render_directory:
        render_pass_list = wizard_tools.get_all_render_passes()

        layer_out_list = [
            layer for layer in wizard_tools.get_all_layer_out()
            if layer.OverrideSettings.get() == 1  # Filtering in layer out nodes
                                                  # with OverrideSettings enabled
        ]

        for node in render_pass_list + layer_out_list:
            node: RenderPass | LayerOut
            old_file_pattern = node.FileName.get()
            if old_file_pattern != '':
                file_pattern = os.path.basename(old_file_pattern)
            else:
                file_pattern = "$L_$n_$o.$05f.$x"
            node.FileName.set(os.path.join(
                render_directory, file_pattern))
        return render_directory


def setup_frame_range(render_type, frame_range=None) -> str:
    if not frame_range:
        frame_range = wizard_communicate.get_frame_range(
            os.environ['wizard_work_env_id'])
    if len(frame_range) == 2:
        frame_range.append(frame_range[1])
        frame_range.insert(0, frame_range[0])
    if render_type == 'FML':
        frames = "{0},{1},{2}".format(frame_range[1], int(
            (frame_range[1]+frame_range[2])/2), frame_range[2])
    elif render_type == 'HD' or render_type == 'LD':
        frames = "{0}-{1}".format(frame_range[1], frame_range[2])
    else:
        logger.info("Unkown render type : {0}".format(render_type))
        frames = None
    if frames is not None:
        with Modifier() as mod:
            preferences_node = wizard_tools.get_node_from_name('Preferences')
            preferences_node.RenderRange.set(frames)

    return frames


def setup_image_format(render_type) -> tuple[int, int] | None:
    image_format = wizard_communicate.get_image_format()
    if render_type == 'LD':
        image_format = [int(image_format[0]/2), int(image_format[1]/2)]
    elif render_type == 'HD' or render_type == 'FML':
        pass
    else:
        logger.info("Unkown render type : {0}".format(render_type))
        image_format = None

    if image_format:
        width = float(image_format[0])
        height = float(image_format[1])
        Document().ProjectWidth.set(width)
        Document().ProjectHeight.set(height)
        Document().ProjectAspectRatio.set(1)
        return (width, height)
    return None


def setup_renderfarm_settings(render_type: str):
    """
    Sets the render farm settings.
    
    Workflow:
        1. RenderfarmSequence attribute: \<project\>_\<render_type\>_\<category\>_\<asset\>
    """
    project = os.environ.get("wizard_project", "")
    category = os.environ.get("wizard_category_name", "")
    asset = os.environ.get("wizard_asset_name", "")

    # Checking if the required environment variables are set
    for prop in ["project", "category", "asset"]:
        value = locals().get(prop, "")
        if not value:
            logger.warning(f"No '{prop}' environment variable set.")
            return

    prefs = guerilla.getpreferences()
    if not prefs:
        logger.error("Could not retrieve Guerilla filescene preferences.")
        return

    plug: guerilla.Plug = prefs.RenderfarmSequence
    if not plug:
        logger.warning("RenderfarmSequence attribute not found in preferences.")
        return

    plug.set(f"{project}_{render_type}_{category}_{asset}")


def setup_FML():
    setup_frame_range('FML')
    setup_image_format('FML')


def setup_HD():
    setup_frame_range('HD')
    setup_image_format('HD')


def setup_LD():
    setup_frame_range('LD')
    setup_image_format('LD')
