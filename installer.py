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
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import shutil
import psutil
import ctypes
import sys
import winreg
import winshell
from win32com.client import Dispatch
import logging
import yaml
import time

# CHECK ADMIN
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def ressources_path(relative_path):
     if hasattr(sys, '_MEIPASS'):
         return os.path.join(sys._MEIPASS, relative_path)
     return os.path.join(os.path.abspath("."), relative_path)

def get_zip_file():
    return ressources_path('__wizard__.zip')

def get_install_dir():
    install_dir = os.path.join(os.environ.get("PROGRAMFILES"), 'Wizard')
    return install_dir

def unpack_zip():
    zip_file = get_zip_file()
    install_dir = get_install_dir()
    if not os.path.isdir(install_dir):
        os.mkdir(install_dir)
        print(f"{install_dir} created")
    shutil.unpack_archive(zip_file, install_dir, 'zip')
    print(f"Wizard files unpacked")

def remove_install_dir():
    install_dir = get_install_dir()
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
        print(f"{install_dir} removed")
    else:
        print(f"{install_dir} not found")

def get_version():
    version_file = ressources_path('version.yaml')
    if os.path.isfile(version_file):
        with open(version_file, 'r') as f:
            version_dic = yaml.load(f, Loader=yaml.Loader)
        return version_dic
    else:
        logging.error(f'{version_file} not found')
        return None

def get_size():
    install_dir = get_install_dir()
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(install_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return int(total_size/1000)

def create_reg_keys():
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    install_dir = get_install_dir()
    version_dic = get_version()
    version = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}.{str(version_dic['builds']).zfill(4)}"

    winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, KEY)

    keys_list = []
    keys_list.append(('UninstallString', winreg.REG_SZ, "{}\\uninstall.exe".format(install_dir)))
    keys_list.append(('DisplayName', winreg.REG_SZ, "Wizard"))
    keys_list.append(('DisplayVersion', winreg.REG_SZ, version))
    keys_list.append(('Publisher', winreg.REG_SZ, "Wizard - Pipeline manager"))
    keys_list.append(('InstallLocation', winreg.REG_SZ, install_dir))
    keys_list.append(('DisplayIcon', winreg.REG_SZ, install_dir+'\\wizard.exe'))
    keys_list.append(('EstimatedSize', winreg.REG_DWORD, get_size()))

    for key in keys_list:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(registry_key, key[0], 0, key[1], key[2])
        winreg.CloseKey(registry_key)
        print(f"{key[0]} registery key created")

def delete_reg_keys():
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE , KEY, 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, KEY)
    winreg.CloseKey(registry_key)
    print(f"Wizard registery keys deleted")

def create_shortcuts():
    create_shortcut('Wizard', 'Wizard.exe')

def delete_shortcuts():
    delete_shortcut('Wizard')
    delete_shortcut('PyWizard')
    delete_shortcut('Wizard Console')
    delete_shortcut('Wizard Server')

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
    print(f"{exe} shortcut created")

def delete_shortcut(name):
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    if os.path.isfile(path):
        os.remove(path)
        print(f"{name} shortcut deleted")

def get_current_install():
    is_reg = None
    version = None
    is_files = None

    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE , KEY, 0, winreg.KEY_READ)
        is_reg = True
        version = winreg.QueryValueEx(registry_key, 'DisplayVersion')[0]
        winreg.CloseKey(registry_key)
    except FileNotFoundError:
        pass
    if os.path.isdir(get_install_dir()):
        is_files = True
    return is_reg, version, is_files

def install():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print(f"Installing...")
        unpack_zip()
        create_reg_keys()
        create_shortcuts()
        print(f"Wizard installed")

def uninstall():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print(f"Uninstalling...")
        remove_install_dir()
        delete_reg_keys()
        delete_shortcuts()
        print(f"Wizard uninstalled")

def update():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        uninstall()
        install()

class installer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(installer, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setWindowIcon(QtGui.QIcon(ressources_path('ressources/icons/wizard_setup.svg')))
        self.setWindowTitle(f"Wizard installer")
        self.build_ui()

    def showEvent(self, event):
        desktop = QtWidgets.QApplication.desktop()
        screenRect = desktop.screenGeometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move((screen_maxX-self.width())/2, (screen_maxY-self.height())/2)

    def process(self):
        version_dic = get_version()
        version = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}.{str(version_dic['builds']).zfill(4)}"
        self.version_label.setText(version)

        is_reg, version, is_files = get_current_install()
        if (is_reg or version or is_files) is not None:
            self.infos_label.setText('Installing Wizard')
            self.progress_bar.setValue(0)
            QtWidgets.QApplication.processEvents()
            time.sleep(1)
            self.infos_label.setText('Removing Wizard files')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(10)
            remove_install_dir()
            self.infos_label.setText('Deleting registery keys')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(30)
            delete_reg_keys()
            self.infos_label.setText('Deleting shortcuts')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(50)
            delete_shortcuts()
            self.infos_label.setText('Unpacking Wizard')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(70)
            unpack_zip()
            self.infos_label.setText('Creating registery keys')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(80)
            create_reg_keys()
            self.infos_label.setText('Creating shortcuts')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(90)
            create_shortcuts()
            self.infos_label.setText('Wizard updated')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(100)
            time.sleep(1)
            sys.exit()
        elif (is_reg and version and is_files) is None:
            self.infos_label.setText('Installing Wizard')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(0)
            time.sleep(1)
            self.infos_label.setText('Unpacking Wizard')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(40)
            unpack_zip()
            self.infos_label.setText('Creating registery keys')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(70)
            create_reg_keys()
            self.infos_label.setText('Creating shortcuts')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(90)
            create_shortcuts()
            self.infos_label.setText('Wizard installed')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(100)
            time.sleep(1)
            sys.exit()

    def build_ui(self):
        self.setStyleSheet('QWidget{background-color:#2c2c33;color:white;}')
        self.setFixedWidth(600)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(18,18,18,18)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setStyleSheet('QFrame{border-radius:10px;}')

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(18)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setContentsMargins(20,20,20,20)
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.datas_widget = QtWidgets.QWidget()
        self.datas_layout = QtWidgets.QHBoxLayout()
        self.datas_layout.setContentsMargins(0,0,0,0)
        self.datas_layout.setSpacing(12)
        self.datas_widget.setLayout(self.datas_layout)
        self.frame_layout.addWidget(self.datas_widget)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.image_label.setPixmap(QtGui.QIcon(ressources_path('ressources/icons/wizard_setup.svg')).pixmap(34))
        self.datas_layout.addWidget(self.image_label)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.datas_layout.addWidget(self.infos_widget)

        self.infos_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.infos_label)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setStyleSheet('color:gray;')
        self.infos_layout.addWidget(self.version_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet('QProgressBar{height:6px;background-color: rgba(0,0,0,50);border-radius:3px;color: transparent;}QProgressBar::chunk {background-color: #7785de;border-radius:3px;}')
        self.progress_bar.setMaximumHeight(6)
        self.frame_layout.addWidget(self.progress_bar)

def main():
    if is_admin():
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
        app = QtWidgets.QApplication(sys.argv)
        installer_widget = installer()
        installer_widget.show()
        QtWidgets.QApplication.processEvents()
        installer_widget.process()
        sys.exit(app.exec_())
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

if __name__ == '__main__':
    main()