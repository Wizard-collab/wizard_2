# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import logging
import os

# Wizard modules
from wizard.vars import user_vars

def get_logger(name=None):
    # create logger
    # Use this module to keep logger format
    # integrity across wizard application
    logger_level = logging.INFO
    logging.basicConfig(level=logger_level,
        format="%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s")
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger()
    create_prefs_folder()
    file_handler = logging.FileHandler(user_vars._user_logger_file_)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s'))
    logger.addHandler(file_handler)
    return logger

def create_prefs_folder():
    if not os.path.isdir(user_vars._user_path_):
        os.mkdir(user_vars._user_path_)