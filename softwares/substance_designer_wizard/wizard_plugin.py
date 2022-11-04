# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
import os
import logging

# Wizard modules
import wizard_communicate
from substance_designer_wizard import wizard_tools
from substance_designer_wizard.export import texturing

# Substance designer modules
import sd

logger = logging.getLogger(__name__)
ctx = sd.getContext()
logger.addHandler(ctx.createRuntimeLogHandler())
logger.propagate = False
logger.setLevel(logging.INFO)

def save():
    wizard_tools.save()

def export():
    stage_name = os.environ['wizard_stage_name']
    if stage_name == 'texturing':
        texturing.main()
    else:
        logger.warning("Unplugged stage : {}".format(stage_name))

def init_scene():
    # Create new empy package
    pkgMgr = wizard_tools.get_packageMgr()
    if wizard_tools.get_wizard_pkg() is not None:
        logger.warning("A wizard scene already exists, skipping init.")
        return
    empty_package = pkgMgr.newUserPackage()
    pkgMgr.savePackageAs(empty_package, wizard_communicate.get_file(os.environ["wizard_version_id"]))
