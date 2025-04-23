# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import logging

# Wizard modules
import wizard_communicate
import wizard_hooks

# Substance designer modules
import sd
from sd.api.sbs.sdsbsarexporter import *

logger = logging.getLogger(__name__)
ctx = sd.getContext()
logger.addHandler(ctx.createRuntimeLogHandler())
logger.propagate = False
logger.setLevel(logging.INFO)


def get_packageMgr():
    ctx = sd.getContext()
    app = ctx.getSDApplication()
    return app.getPackageMgr()


def get_SDSBSARExporter():
    ctx = sd.getContext()
    app = ctx.getSDApplication()
    return SDSBSARExporter(ctx, None)


def get_wizard_pkg():
    file = wizard_communicate.get_file(os.environ["wizard_version_id"])
    pkgMgr = get_packageMgr()
    pkg = pkgMgr.getUserPackageFromFilePath(file)
    return pkg


def save_or_save_increment():
    pkg = get_wizard_pkg()
    if pkg is None:
        logger.warning(
            "Wizard package not found, try to init the scene first.")
        return
    pkgMgr = get_packageMgr()
    pkgMgr.savePackage(pkg)
    return pkg.getFilePath()


def save():
    file_path, version_id = wizard_communicate.add_version(
        int(os.environ['wizard_work_env_id']))
    if not (file_path and version_id):
        logger.warning("Can't save increment")
        return
    logger.info("Saving file {}".format(file_path))
    pkg = get_wizard_pkg()
    if not pkg:
        logger.warning(
            "Wizard package not found, try to init the scene first.")
        return
    get_packageMgr().savePackageAs(pkg, file_path)
    os.environ['wizard_version_id'] = str(version_id)
    trigger_after_save_hook(file_path)
    return file_path


def trigger_after_save_hook(scene_path):
    stage_name = os.environ['wizard_stage_name']
    string_asset = wizard_communicate.get_string_variant_from_work_env_id(
        int(os.environ['wizard_work_env_id']))
    return wizard_hooks.after_save_hooks('substance_designer', stage_name, string_asset, scene_path)
