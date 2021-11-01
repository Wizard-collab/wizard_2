# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Python modules
import os
import shutil
import ctypes
import sys
import winreg
import winshell
from win32com.client import Dispatch
import logging

# Wizard modules
from wizard.core import application

# CHECK ADMIN
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_zip_file():
    version_dic = application.get_version()
    release_name = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}"
    zip_file = os.path.join('compile', f"{release_name}_{str(version_dic['builds']).zfill(4)}.zip")
    return zip_file

def get_install_dir():
    install_dir = os.path.join(os.environ.get("PROGRAMFILES"), 'Wizard')
    return install_dir

def unpack_zip():
    zip_file = get_zip_file()
    install_dir = get_install_dir()
    if not os.path.isdir(install_dir):
        os.mkdir(install_dir)
    shutil.unpack_archive(zip_file, install_dir, 'zip')

def remove_install_dir():
    install_dir = get_install_dir()
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
        logging.info(f"{install_dir} removed")
    else:
        logging.info(f"{install_dir} not found")

def create_reg_keys():
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    install_dir = get_install_dir()
    version_dic = application.get_version()
    version = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}"

    winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, KEY)

    keys_list = []
    keys_list.append(('UninstallString', "{}\\uninstall.exe".format(install_dir)))
    keys_list.append(('DisplayName', "Wizard"))
    keys_list.append(('DisplayVersion', version))
    keys_list.append(('Publisher', "Wizard - Pipeline manager"))
    keys_list.append(('InstallLocation', install_dir))
    keys_list.append(('DisplayIcon', install_dir+'\\wizard.exe'))

    for key in keys_list:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(registry_key, key[0], 0, winreg.REG_SZ, key[1])
        winreg.CloseKey(registry_key)

def delete_reg_keys():
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE , KEY, 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, KEY)
    winreg.CloseKey(registry_key)

def create_shortcuts():
    create_shortcut('Wizard', 'Wizard.exe')

def delete_shortcuts():
    delete_shortcut('Wizard')

def create_shortcut(name, exe):
    install_dir = get_install_dir()
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    target = os.path.join(install_dir, exe)
    wDir = install_dir
    icon = os.path.join(install_dir, exe)
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()

def delete_shortcut(name):
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    if os.path.isfile(path):
        os.remove(path)

def install():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        unpack_zip()
        create_reg_keys()
        create_shortcuts()

def uninstall():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        remove_install_dir()
        delete_reg_keys()
        delete_shortcuts()

def replace():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        uninstall()
        install()