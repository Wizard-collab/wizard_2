# coding: utf-8
# Author: Mael PERON
# Contact: maelperon.cg@gmail.com

# Python modules
import os
import sys
import venv
import subprocess


def ensure_venv():
    """ Create a virtual environment for the wizard plugin if it does not exist and add it to sys.path. """
    venv_path = os.path.expanduser("~/Documents/wizard/blender/.venv")

    _venv = venv.EnvBuilder(with_pip=True)
    if not os.path.exists(venv_path):
        _venv.create(venv_path)

    site_packages_path = os.path.join(venv_path, "Lib", "site-packages")

    if site_packages_path not in sys.path:
        sys.path.append(site_packages_path)


def install_package(package_name):
    """ Install a package in the virtual environment. """
    venv_path = os.path.expanduser("~/Documents/wizard/blender/.venv")
    pip_executable = os.path.join(venv_path, "Scripts", "pip.exe")

    process = subprocess.Popen([pip_executable, "install", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    if process.returncode != 0:
        raise Exception(f"Failed to install package {package_name}. Error: {stderr}")