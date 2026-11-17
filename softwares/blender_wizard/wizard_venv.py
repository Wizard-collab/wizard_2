# coding: utf-8
# Author: Mael PERON
# Contact: maelperon.cg@gmail.com

# Python modules
import os
import sys
import venv
import subprocess
import logging
import importlib.metadata
import sysconfig
from pathlib import Path

logger = logging.getLogger(__name__)


def get_venv_path(*subdirectories):
    """ Get the path to the virtual environment (and its subdirectories) for the wizard plugin. """
    venv_path = Path.home() / "Documents" / "wizard" / "blender" / ".venv"
    venv_path = venv_path.joinpath(*subdirectories)
    logger.debug(f"Virtual environment path: {venv_path}")
    return os.fspath(venv_path)


def get_venv_site_packages_path():
    """Get the site-packages path for the virtual environment."""
    venv_path = get_venv_path()
    site_packages_path = sysconfig.get_path(
        "purelib",
        vars={"base": venv_path, "platbase": venv_path},
    )
    logger.debug(f"Virtual environment site-packages path: {site_packages_path}")
    return site_packages_path


def get_venv_pip_path():
    """Get the platform-specific pip executable path for the virtual environment."""
    bin_directory = "Scripts" if os.name == "nt" else "bin"
    pip_executable = "pip.exe" if os.name == "nt" else "pip"
    return get_venv_path(bin_directory, pip_executable)


def ensure_venv():
    """ Create a virtual environment for the wizard plugin if it does not exist and add it to sys.path. """
    venv_path = get_venv_path()

    _venv = venv.EnvBuilder(with_pip=True)
    if not os.path.exists(venv_path):
        logger.info(f"Creating virtual environment at {venv_path}")
        _venv.create(venv_path)
    else:
        logger.debug(f"Virtual environment already exists at {venv_path}")

    site_packages_path = get_venv_site_packages_path()

    if site_packages_path not in sys.path:
        logger.debug(f"Adding virtual environment site-packages to sys.path: {site_packages_path}")
        sys.path.append(site_packages_path)
    else:
        logger.debug("Virtual environment site-packages already in sys.path")


def is_package_installed(package_name):
    """ Check whether a package is installed in the virtual environment. """
    logger.debug(f"Checking whether package '{package_name}' is installed")
    try:
        importlib.metadata.distribution(package_name)
        logger.info(f"Package '{package_name}' is already installed")
        return True
    except importlib.metadata.PackageNotFoundError:
        logger.warning(f"Package '{package_name}' is not installed")
        return False


def install_package(package_name):
    """ Install a package in the virtual environment. """
    if is_package_installed(package_name):
        return

    pip_executable = get_venv_pip_path()
    logger.info(f"Installing package '{package_name}'")
    logger.debug(f"Using pip executable: {pip_executable}")
    if not os.path.isfile(pip_executable):
        logger.warning(f"pip executable was not found: {pip_executable}")
        raise Exception(f"pip executable was not found: {pip_executable}")

    process = subprocess.Popen([pip_executable, "install", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    if process.returncode != 0:
        logger.warning(f"Failed to install package '{package_name}': {stderr.strip()}")
        raise Exception(f"Failed to install package {package_name}. Error: {stderr}")
    logger.info(f"Successfully installed package '{package_name}'")