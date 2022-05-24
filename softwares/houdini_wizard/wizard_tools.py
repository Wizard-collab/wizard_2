# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import traceback
import logging
logger = logging.getLogger(__name__)

# Houdini modules
import hou

# Wizard modules
import wizard_communicate

def save_increment():
    file_path, version_id = wizard_communicate.add_version(int(os.environ['wizard_work_env_id']))
    if file_path and version_id:
        logger.debug("Saving file {}".format(file_path))
        hou.hipFile.save(file_name=file_path)
        os.environ['wizard_version_id'] = str(version_id)
    else:
        logger.warning("Can't save increment")
