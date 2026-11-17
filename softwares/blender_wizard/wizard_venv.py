# coding: utf-8
# Author: Mael PERON
# Contact: maelperon.cg@gmail.com

# Python modules
import os
import sys
import venv
import subprocess
import importlib.metadata


def get_venv_path(*subdirectories):
    """ Get the path to the virtual environment (and its subdirectories) for the wizard plugin. """
    venv_path = os.path.expanduser("~/Documents/wizard/blender/.venv")
    for arg in subdirectories:
        venv_path = os.path.join(venv_path, arg)
    return venv_path


def ensure_venv():
    """ Create a virtual environment for the wizard plugin if it does not exist and add it to sys.path. """
    venv_path = get_venv_path()

    _venv = venv.EnvBuilder(with_pip=True)
    if not os.path.exists(venv_path):
        _venv.create(venv_path)

    site_packages_path = os.path.join(venv_path, "Lib", "site-packages")

    if site_packages_path not in sys.path:
        sys.path.append(site_packages_path)


def is_package_installed(package_name):
    """ Check whether a package is installed in the virtual environment. """
    try:
        importlib.metadata.distribution(package_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def install_package(package_name):
    """ Install a package in the virtual environment. """
    if is_package_installed(package_name):
        return

    pip_executable = get_venv_path("Scripts", "pip.exe")

    process = subprocess.Popen([pip_executable, "install", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    if process.returncode != 0:
        raise Exception(f"Failed to install package {package_name}. Error: {stderr}")