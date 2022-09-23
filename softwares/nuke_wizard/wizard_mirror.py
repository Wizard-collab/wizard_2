# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import shutil
import traceback
import time
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import nuke
import nukescripts

# Wizard modules
import wizard_communicate
from nuke_wizard.widgets import mirror_loading_widget 

class mirror_files_to_local():
    def __init__(self, files_list):
        self.files_list = files_list

    def mirror(self):
        if len(self.files_list) == 0:
            return
        if nuke.GUI:
            self.mirror_loading_widget = mirror_loading_widget.mirror_loading_widget()
            self.mirror_loading_widget.set_title("Mirroring files to local")
            self.mirror_loading_widget.show()
        logger.info("Mirroring files to local")
        progress = 0 
        progress_step = 100/len(self.files_list)

        local_files_list = []
        local_path = wizard_communicate.get_local_path()
        project_path = wizard_communicate.get_project_path()
        if local_path is None or local_path == '':
            logger.warning("Local path not setted, keeping project files. It is recommended to set a local path in wizard.")
            return local_files_list
        for file in self.files_list:
            local_file = replace_project_path_with_local_path(file, project_path, local_path)
            if not os.path.isdir(os.path.dirname(local_file)):
                os.makedirs(os.path.dirname(local_file))
            if not os.path.isfile(local_file):
                if nuke.GUI:
                    self.mirror_loading_widget.set_info(f"Copying {os.path.basename(file)}...")
                logger.info(f"Copying {os.path.basename(file)}...")
                shutil.copyfile(file, local_file)
            else:
                if nuke.GUI:
                    self.mirror_loading_widget.set_info(f"{os.path.basename(file)} already exists, skipping")
                logger.info(f"{os.path.basename(file)} already exists, skipping")
            progress += progress_step
            if nuke.GUI:
                self.mirror_loading_widget.set_progress(progress)
            logger.info(f"Mirror progress : {int(progress)}%")
            local_files_list.append(local_file)
        return local_files_list

def replace_project_path_with_local_path(file, project_path, local_path):
    return local_path+file[len(project_path):]
