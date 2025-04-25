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

"""
This module provides functionality for uninstalling the Wizard application on Windows.

It includes:
- Functions to check administrative privileges, manage registry keys, and delete files.
- A PyQt-based GUI for user interaction during the uninstallation process.
- A bootstrap mechanism to ensure the script runs in the correct context.

Main Components:
1. Helper Functions:
    - `is_bootsrap()`: Determines if the script is running in a bootstrap context.
    - `create_bootstrap()`: Creates a temporary bootstrap executable.
    - `is_admin()`: Checks if the user has administrative privileges.
    - `ressources_path()`: Resolves resource paths for bundled applications.
    - `remove_install_dir()`: Deletes the installation directory.
    - `delete_reg_keys()`: Removes registry keys related to the application.
    - `delete_shortcuts()` and `delete_shortcut()`: Deletes desktop shortcuts.
    - `get_current_install()`: Retrieves installation details from the registry.

2. Main Uninstallation Logic:
    - `uninstall()`: Handles the uninstallation process, including privilege escalation.

3. PyQt GUI:
    - `uninstaller`: A QWidget-based class for the uninstaller GUI.
    - Provides a progress bar, status messages, and buttons for user interaction.

4. Entry Point:
    - `main()`: Determines the execution context and starts the uninstallation process.

Note:
- The script is designed for Windows and requires administrative privileges.
- It uses PyQt6 for the GUI and interacts with the Windows registry and file system.
"""

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


def is_bootsrap():
    """
    Determines whether the script is running in a "bootstrap" context.

    This function checks several conditions to identify if the script is being executed
    in a specific environment or directory structure that indicates a bootstrap state.

    Returns:
        bool: 
            - True if the script is running in a bootstrap context or if the script's 
              filename ends with '.py'.
            - False if the script is not in a bootstrap context and is running from 
              specific directories  like the current installation path.
    """
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
    """
    Creates a temporary bootstrap executable for the uninstallation process.

    This function performs the following steps:
    1. Creates a temporary directory.
    2. Checks if the current script is not a Python file (i.e., not ending with '.py').
    3. Copies the current executable to the temporary directory as 'uninstall.exe'.
    4. Changes the working directory to the temporary directory.
    5. Starts the copied executable ('uninstall.exe') from the temporary directory.
    6. Exits the current script.

    Note:
    - This function is designed to handle cases where the script is packaged as an executable.
    - It ensures that the uninstallation process runs from a temporary location.

    Raises:
    - SystemExit: Terminates the current script after starting the bootstrap executable.
    """
    tempdir = tempfile.mkdtemp()
    if not sys.argv[0].endswith('.py'):
        bootstrap = os.path.join(tempdir, 'uninstall.exe')
        shutil.copyfile(os.path.join(
            os.path.abspath(''), sys.argv[0]), bootstrap)
        os.chdir(tempdir)
        os.startfile(bootstrap)
        sys.exit()


def is_admin():
    """
    Checks if the current user has administrative privileges.

    Returns:
        bool: True if the user has administrative privileges, False otherwise.
              If an exception occurs during the check, it will return False.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def ressources_path(relative_path):
    """
    Get the absolute path to a resource, handling cases where the script is 
    bundled using PyInstaller.

    If the script is running in a PyInstaller bundle, the resource path is 
    resolved relative to the `_MEIPASS` directory. Otherwise, it is resolved 
    relative to the current working directory.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def remove_install_dir():
    """
    Removes the installation directory of the Wizard application.

    This function retrieves the current installation directory using the 
    `get_current_install` function. If the directory exists, it deletes 
    the entire directory and its contents. If the directory does not exist, 
    it prints a message indicating that the directory was not found.

    Note:
    - This function uses `shutil.rmtree` to remove the directory, which 
      deletes all files and subdirectories within the specified directory.

    Raises:
    - OSError: If an error occurs during the removal of the directory.
    """
    install_dir = get_current_install()[3]
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
        print(f"{install_dir} removed")
    else:
        print(f"{install_dir} not found")


def delete_reg_keys():
    """
    Deletes specific registry keys related to the "Wizard" application from the Windows registry.

    This function targets the registry path:
    "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    under HKEY_LOCAL_MACHINE and removes it. It requires administrative privileges
    to execute successfully.

    Raises:
        FileNotFoundError: If the specified registry key does not exist.
        PermissionError: If the function lacks the necessary permissions to modify the registry.

    Note:
        Ensure that the `winreg` module is imported and that the script is run with
        administrative privileges to avoid errors.
    """
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    registry_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, KEY)
    winreg.CloseKey(registry_key)
    print(f"Wizard registery keys deleted")


def delete_shortcuts():
    """
    Deletes specific shortcuts related to the Wizard application from the desktop.

    This function targets the following shortcuts:
    - 'Wizard'
    - 'PyWizard'
    - 'server'
    - 'Create Repository'
    - 'Change Repository'

    If any of these shortcuts exist on the desktop, they will be removed.

    Note:
    - This function uses the `delete_shortcut` helper function to remove each shortcut.
    - Ensure that the `winshell` module is properly installed and accessible.
    """
    delete_shortcut('Wizard')
    delete_shortcut('PyWizard')
    delete_shortcut('server')
    delete_shortcut('Create Repository')
    delete_shortcut('Change Repository')


def delete_shortcut(name):
    """
    Deletes a shortcut file from the desktop.

    This function locates a shortcut file with the specified name
    on the user's desktop and deletes it if it exists.

    Args:
        name (str): The name of the shortcut (without the .lnk extension).

    Returns:
        None

    Side Effects:
        - Removes the shortcut file from the desktop if it exists.
        - Prints a message indicating the shortcut was deleted.

    Raises:
        None
    """
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    if os.path.isfile(path):
        os.remove(path)
        print(f"{name} shortcut deleted")


def get_current_install():
    """
    Retrieves information about the current installation of the Wizard application 
    from the Windows registry and checks the existence of the installation directory.
    Returns:
        tuple: A tuple containing the following:
            - is_reg (bool or None): True if the registry key for the application exists, 
              otherwise None.
            - version (str or None): The version of the application as retrieved from the 
              registry, or None if not found.
            - is_files (bool or None): True if the installation directory exists, otherwise None.
            - install_dir (str or None): The path to the installation directory as retrieved 
              from the registry, or None if not found.
    """
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
    """
    Handles the uninstallation process for the wizard application.

    This function checks if the script is running with administrative privileges.
    If not, it attempts to restart itself with elevated permissions. Once running
    as an administrator, it performs the following steps:

    1. Removes the installation directory.
    2. Deletes associated registry keys.
    3. Deletes any created shortcuts.

    Finally, it prints a confirmation message indicating the uninstallation is complete.

    Note:
        - This function assumes the presence of helper functions:
          `is_admin()`, `remove_install_dir()`, `delete_reg_keys()`, and `delete_shortcuts()`.
        - It uses `ctypes` and `sys` modules to handle privilege escalation on Windows.
    """
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
    """
    A QWidget-based class for the Wizard uninstaller GUI.
    This class provides a graphical interface to uninstall the Wizard application. 
    It includes functionality to display the current version, show progress during 
    the uninstallation process, and handle user interactions.
    Methods:
        __init__(parent=None):
            Initializes the uninstaller widget, sets up the UI, and connects signals to slots.
        showEvent(event):
            Centers the widget on the primary screen when it is shown.
        fill_ui():
            Fills the UI with the current installed version of the Wizard application.
        process():
            Executes the uninstallation process, including removing files, deleting registry keys, 
            and removing shortcuts. Updates the progress bar and status messages during the process.
        connect_functions():
            Connects button click events to their respective functions.
        build_ui():
            Constructs the user interface, including layouts, labels, progress bar, and buttons.
    Attributes:
        main_layout (QtWidgets.QVBoxLayout): The main layout of the widget.
        datas_widget (QtWidgets.QWidget): A widget containing the image and information layout.
        datas_layout (QtWidgets.QHBoxLayout): The layout for the datas_widget.
        image_label (QtWidgets.QLabel): A label displaying the Wizard icon.
        infos_widget (QtWidgets.QWidget): A widget containing the information layout.
        infos_layout (QtWidgets.QVBoxLayout): The layout for the infos_widget.
        infos_label (QtWidgets.QLabel): A label displaying the current status or prompt.
        version_label (QtWidgets.QLabel): A label displaying the current installed version.
        progress_bar (QtWidgets.QProgressBar): A progress bar to show uninstallation progress.
        buttons_widget (QtWidgets.QWidget): A widget containing the buttons layout.
        buttons_layout (QtWidgets.QHBoxLayout): The layout for the buttons_widget.
        cancel_button (QtWidgets.QPushButton): A button to cancel the uninstallation process.
        uninstall_button (QtWidgets.QPushButton): A button to start the uninstallation process.
        close_button (QtWidgets.QPushButton): A button to close the uninstaller after completion.
    """

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
    """
    Entry point for the uninstaller script.

    This function determines the execution context and handles the uninstallation process:
    1. Checks if the script is running in a bootstrap context using `is_bootsrap()`.
    2. If running in a bootstrap context:
        - Checks if the script has administrative privileges using `is_admin()`.
        - If it has admin privileges, initializes the PyQt application, applies the stylesheet,
          and displays the uninstaller GUI.
        - If not, restarts the script with elevated privileges.
    3. If not running in a bootstrap context, creates a temporary bootstrap executable
       using `create_bootstrap()`.

    Note:
    - This function ensures that the uninstallation process is executed with the necessary
      permissions and in the correct environment.
    - The script exits after the PyQt application is closed or after restarting with admin privileges.
    """
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
