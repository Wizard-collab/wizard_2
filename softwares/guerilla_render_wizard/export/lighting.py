# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Guerilla modules
import guerilla

# Python modules
import traceback
import os
import logging
logger = logging.getLogger(__name__)

# Wizard modules
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_export
import wizard_communicate

def main():
    scene = wizard_export.save_or_save_increment()
    try:
        export_name = 'main'
        render_directory = wizard_export.prepare_render('lighting', export_name)
        if render_directory:
            file_pattern = "$L_$n_$o.$05f.$x"
            render_pass_list = wizard_tools.get_all_render_passes()
            for render_pass in render_pass_list:
                render_pass.FileName.set(os.path.join(render_directory, file_pattern))

            frame_range = wizard_communicate.get_frame_range(os.environ['wizard_work_env_id'])
            preferences_node = wizard_tools.get_node_from_name('Preferences')
            preferences_node.RenderRange.set('{0}-{1}'.format(frame_range[1], frame_range[2]))

            guerilla.render('batch', None)

    except:
        logger.error(str(traceback.format_exc()))
