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
from PyQt6 import QtWidgets, QtGui
import os
import shutil
import ctypes
import sys
import winreg
import winshell
from win32com.client import Dispatch
import time
import tempfile

# CHECK ADMIN


def is_bootsrap():
    if not sys.argv[0].endswith('.py'):
        if os.path.normpath(os.path.abspath('')) != os.path.normpath(get_current_install()[3]):
            if os.path.normpath(os.path.abspath('')) == os.path.normpath('C:/Windows/ImmersiveControlPanel'):
                return False
            else:
                return True
        else:
            return False
    else:
        return True


def create_bootstrap():
    tempdir = tempfile.mkdtemp()
    if not sys.argv[0].endswith('.py'):
        bootstrap = os.path.join(tempdir, 'uninstall.exe')
        shutil.copyfile(os.path.join(
            os.path.abspath(''), sys.argv[0]), bootstrap)
        os.chdir(tempdir)
        os.startfile(bootstrap)
        sys.exit()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def ressources_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def remove_install_dir():
    install_dir = get_current_install()[3]
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
        print(f"{install_dir} removed")
    else:
        print(f"{install_dir} not found")


def delete_reg_keys():
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    registry_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, KEY)
    winreg.CloseKey(registry_key)
    print(f"Wizard registery keys deleted")


def delete_shortcuts():
    delete_shortcut('Wizard')
    delete_shortcut('PyWizard')
    delete_shortcut('server')
    delete_shortcut('Create Repository')
    delete_shortcut('Change Repository')


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
    install_dir = None

    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_READ)
        is_reg = True
        version = winreg.QueryValueEx(registry_key, 'DisplayVersion')[0]
        install_dir = winreg.QueryValueEx(registry_key, 'InstallLocation')[0]
        if os.path.isdir(install_dir):
            is_files = True
        winreg.CloseKey(registry_key)
    except FileNotFoundError:
        pass

    return is_reg, version, is_files, install_dir


def uninstall():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print(f"Uninstalling...")
        remove_install_dir()
        delete_reg_keys()
        delete_shortcuts()
        print(f"Wizard uninstalled")


class uninstaller(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(uninstaller, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon(ressources_path(
            'ressources/icons/wizard_setup.png')))
        self.setWindowTitle(f"Wizard uninstaller")

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def showEvent(self, event):
        desktop = QtGui.QGuiApplication.primaryScreen()
        screenRect = desktop.geometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move(int((screen_maxX-self.width())/2),
                  int((screen_maxY-self.height())/2))
        print(os.path.abspath(''))

    def fill_ui(self):
        version = get_current_install()[1]
        self.version_label.setText(version)

    def process(self):
        is_reg, version, is_files, install_dir = get_current_install()
        if (is_reg or version or is_files) is not None:
            self.infos_label.setText('Uninstalling Wizard')
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
            self.infos_label.setText('Wizard uninstalled')
            QtWidgets.QApplication.processEvents()
            self.progress_bar.setValue(100)

            self.cancel_button.setVisible(0)
            self.uninstall_button.setVisible(0)
            self.close_button.setVisible(1)

    def connect_functions(self):
        self.cancel_button.clicked.connect(sys.exit)
        self.close_button.clicked.connect(sys.exit)
        self.uninstall_button.clicked.connect(self.process)

    def build_ui(self):
        self.setFixedWidth(600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.datas_widget = QtWidgets.QWidget()
        self.datas_layout = QtWidgets.QHBoxLayout()
        self.datas_layout.setContentsMargins(0, 0, 0, 0)
        self.datas_layout.setSpacing(12)
        self.datas_widget.setLayout(self.datas_layout)
        self.main_layout.addWidget(self.datas_widget)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.image_label.setPixmap(QtGui.QIcon(ressources_path(
            'ressources/icons/wizard_setup.png')).pixmap(34))
        self.datas_layout.addWidget(self.image_label)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0, 0, 0, 0)
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.datas_layout.addWidget(self.infos_widget)

        self.infos_label = QtWidgets.QLabel('Uninstall ?')
        self.infos_layout.addWidget(self.infos_label)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setStyleSheet('color:gray;')
        self.infos_layout.addWidget(self.version_label)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet(
            'QProgressBar{height:6px;background-color: rgba(0,0,0,50);border-radius:3px;color: transparent;}QProgressBar::chunk {background-color: #7785de;border-radius:3px;}')
        self.progress_bar.setMaximumHeight(6)
        self.main_layout.addWidget(self.progress_bar)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.buttons_layout.addWidget(self.cancel_button)

        self.uninstall_button = QtWidgets.QPushButton('Uninstall')
        self.uninstall_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.uninstall_button)

        self.close_button = QtWidgets.QPushButton('Close')
        self.close_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.close_button)
        self.close_button.setVisible(0)


stylesheet = """
#title_label_2{
    font: bold large;
    font-size: 14px;}
QWidget{background-color:#2c2c33;color:white;}
QPushButton, QToolButton, #classic_button{
    border: 2px solid #42424d;
    background-color: #42424d;
    padding: 12px;
    border-radius: 5px;}
#blue_button{
    background-color: transparent;
    border: 2px solid #7785de;}
#blue_button::hover{
    background-color: #8e9dfa;
    border: 2px solid #8e9dfa;}
#blue_button::pressed{
    background-color: #6772b5;
    border: 2px solid #6772b5;}
QProgressBar{height:6px;background-color: rgba(0,0,0,50);
    border-radius:3px;color: transparent;}
QProgressBar::chunk {background-color:
    #7785de;border-radius:3px;}
"""


def main():
    if is_bootsrap():
        if is_admin():
            os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0.75"
            app = QtWidgets.QApplication(sys.argv)
            app.setStyleSheet(stylesheet)
            uninstaller_widget = uninstaller()
            uninstaller_widget.show()
            QtWidgets.QApplication.processEvents()
            sys.exit(app.exec())
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        create_bootstrap()


if __name__ == '__main__':
    main()
