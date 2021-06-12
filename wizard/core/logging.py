# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import logging

# Wizard modules
from wizard.vars import user_vars

def get_logger(name=None):
    # create logger
    # Use this module to keep logging format
    # integrity across wizard application
    logging_level = logging.INFO
    logging.basicConfig(level=logging_level,
        format="%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s")
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger()
    #file_handler = logging.FileHandler(user_vars._user_logging_file_)
    #file_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)-23.23s] [%(levelname)-5.5s] %(message)s'))
    #logger.addHandler(file_handler)
    return logger
