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
This module provides a comprehensive installation and uninstallation framework for the Wizard application.
It includes functionalities for managing installation directories, creating and deleting registry keys,
handling desktop shortcuts, and providing a graphical user interface (GUI) for the installation process.

Key Features:
- Administrative privilege checks for secure operations.
- Installation and uninstallation of the Wizard application.
- Registry key management for Windows systems.
- Desktop shortcut creation and deletion.
- GUI-based installer using PyQt6 for user interaction.
- Error handling and logging for troubleshooting.

Dependencies:
- PyQt6: For GUI components.
- ctypes: For administrative privilege checks.
- winreg: For Windows registry operations.
- winshell: For desktop shortcut management.
- shutil, os, sys, yaml, logging: For file and system operations.

Usage:
- Run the script to launch the installer GUI.
- The GUI provides options to install, update, or uninstall the Wizard application.
- Ensure the script is executed with administrative privileges for full functionality.

Note:
- This script is designed for Windows systems and may not work on other platforms.
- Use with caution as it modifies system-level settings like the Windows registry.
"""

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
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
import traceback


def is_admin():
    """
    Checks if the current user has administrative privileges.

    Returns:
        bool: True if the user has administrative privileges, False otherwise.
              If an exception occurs during the check, it defaults to False.

    Note:
        This function uses the `ctypes` library to call the Windows API 
        function `IsUserAnAdmin`. It is specific to Windows systems.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def ressources_path(relative_path):
    """
    Get the absolute path to a resource, whether the script is running in a 
    standalone PyInstaller bundle or in a normal Python environment.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_zip_file():
    """
    Returns the absolute path to the Wizard zip file.

    This function assumes the zip file is named '__wizard__.zip' 
    and is located in the resources directory.

    Returns:
        str: The absolute path to the '__wizard__.zip' file.
    """
    return ressources_path('__wizard__.zip')


def get_install_dir():
    """
    Get the installation directory for the Wizard application.

    Returns:
        str: The absolute path to the installation directory, 
                which is located in the "Program Files" directory.
    """
    install_dir = os.path.join(os.environ.get("PROGRAMFILES"), 'Wizard')
    return install_dir


def unpack_zip():
    """
    Unpacks the Wizard zip file into the installation directory.

    This function retrieves the path to the zip file and the installation
    directory. If the installation directory does not exist, it creates it.
    Then, it unpacks the contents of the zip file into the installation directory.

    Raises:
        Any exceptions raised by `shutil.unpack_archive` or `os.mkdir` will propagate.
    """
    zip_file = get_zip_file()
    install_dir = get_install_dir()
    if not os.path.isdir(install_dir):
        # Create the installation directory if it doesn't exist
        os.mkdir(install_dir)
        print(f"{install_dir} created")
    shutil.unpack_archive(zip_file, install_dir, 'zip')  # Unpack the zip file
    print(f"Wizard files unpacked")


def remove_install_dir():
    """
    Removes the installation directory if it exists.

    This function retrieves the installation directory path using the 
    `get_install_dir` function. If the directory exists and is a valid 
    directory, it deletes the directory and its contents using `shutil.rmtree`. 
    If the directory does not exist, it prints a message indicating that the 
    directory was not found.

    Note:
        Ensure that `get_install_dir` is defined and returns the correct 
        installation directory path. Also, be cautious when using 
        `shutil.rmtree` as it will permanently delete the directory and its 
        contents.

    Raises:
        OSError: If an error occurs while attempting to remove the directory.

    Prints:
        A message indicating whether the directory was removed or not found.
    """
    install_dir = get_install_dir()
    if os.path.isdir(install_dir):
        shutil.rmtree(install_dir)
        print(f"{install_dir} removed")
    else:
        print(f"{install_dir} not found")


def get_version():
    """
    Retrieves the version information from a YAML file.

    This function looks for a file named 'version.yaml' in the 'ressources' 
    directory. If the file exists, it reads and parses the YAML content 
    into a dictionary and returns it. If the file does not exist, it logs 
    an error message and returns None.

    Returns:
        dict: A dictionary containing version information if the file exists 
              and is successfully parsed.
        None: If the file does not exist or cannot be accessed.

    Logs:
        Logs an error message if the 'version.yaml' file is not found.
    """
    version_file = ressources_path('ressources/version.yaml')
    if os.path.isfile(version_file):
        with open(version_file, 'r') as f:
            version_dic = yaml.load(f, Loader=yaml.Loader)
        return version_dic
    else:
        logging.error(f'{version_file} not found')
        return None


def get_size():
    """
    Calculates the total size of all files in the installation directory.
    This function traverses through the directory tree of the installation 
    directory, summing up the sizes of all files (excluding symbolic links). 
    The total size is returned in kilobytes (KB).
    Returns:
        int: The total size of all files in the installation directory, in kilobytes (KB).
    """
    install_dir = get_install_dir()
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(install_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return int(total_size/1000)


def create_reg_keys():
    """
    Creates registry keys for the Wizard application in the Windows registry.
    This function sets up the necessary registry entries under the 
    "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard" 
    path to allow the application to appear in the "Programs and Features" section 
    of the Windows Control Panel. It includes details such as uninstall command, 
    display name, version, publisher, installation location, display icon, and 
    estimated size.
    The function performs the following steps:
    1. Retrieves the installation directory and version information.
    2. Creates the registry key if it does not already exist.
    3. Adds multiple subkeys with relevant application information.
    Registry Keys Created:
    - UninstallString: Path to the uninstaller executable.
    - DisplayName: Name of the application.
    - DisplayVersion: Version of the application.
    - Publisher: Publisher information.
    - InstallLocation: Directory where the application is installed.
    - DisplayIcon: Path to the application's icon.
    - EstimatedSize: Estimated size of the application in KB.
    Note:
    - This function requires administrative privileges to modify the Windows registry.
    - Ensure the `get_install_dir`, `get_version`, and `get_size` helper functions 
      are implemented and return valid data.
    Raises:
        OSError: If there is an issue accessing or modifying the registry.
    """
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    install_dir = get_install_dir()
    version_dic = get_version()
    version = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}.{str(version_dic['builds']).zfill(4)}"

    winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, KEY)

    keys_list = []
    keys_list.append(('UninstallString', winreg.REG_SZ,
                     "{}\\uninstall.exe".format(install_dir)))
    keys_list.append(('DisplayName', winreg.REG_SZ, "Wizard"))
    keys_list.append(('DisplayVersion', winreg.REG_SZ, version))
    keys_list.append(('Publisher', winreg.REG_SZ, "Wizard - Pipeline manager"))
    keys_list.append(('InstallLocation', winreg.REG_SZ, install_dir))
    keys_list.append(('DisplayIcon', winreg.REG_SZ,
                     install_dir+'\\wizard.exe'))
    keys_list.append(('EstimatedSize', winreg.REG_DWORD, get_size()))

    for key in keys_list:
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(registry_key, key[0], 0, key[1], key[2])
        winreg.CloseKey(registry_key)
        print(f"{key[0]} registery key created")


def delete_reg_keys():
    """
    Deletes the registry keys for the Wizard application.

    This function removes the registry entry for the Wizard application 
    from the Windows registry under the path 
    "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard".

    Note:
        - This function requires administrative privileges to modify the Windows registry.
        - Be cautious when deleting registry keys, as improper modifications can 
          affect system stability.

    Raises:
        OSError: If there is an issue accessing or modifying the registry.

    Prints:
        A message indicating that the registry keys for Wizard have been deleted.
    """
    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    registry_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, KEY)
    winreg.CloseKey(registry_key)
    print(f"Wizard registery keys deleted")


def create_shortcuts():
    """
    Creates desktop shortcuts for the Wizard application and its related executables.

    This function generates shortcuts for the following executables:
    - Wizard.exe
    - server.exe
    - Create Repository.exe
    - Change Repository.exe

    The shortcuts are created on the user's desktop and point to the respective
    executables in the installation directory.

    Note:
        Ensure that the `create_shortcut` function is implemented and correctly
        handles the creation of shortcuts.

    Raises:
        Any exceptions raised by the `create_shortcut` function will propagate.

    Prints:
        A message indicating the creation of each shortcut.
    """
    create_shortcut('Wizard', 'Wizard.exe')
    create_shortcut('Server', 'server.exe')
    create_shortcut('Create Repository', 'Create Repository.exe')
    create_shortcut('Change Repository', 'Change Repository.exe')


def delete_shortcuts():
    """
    Deletes desktop shortcuts for the Wizard application and its related executables.

    This function removes the shortcuts for the following executables:
    - Wizard
    - PyWizard
    - Server
    - Create Repository
    - Change Repository

    The shortcuts are located on the user's desktop and are deleted if they exist.

    Note:
        Ensure that the `delete_shortcut` function is implemented and correctly
        handles the deletion of shortcuts.

    Raises:
        Any exceptions raised by the `delete_shortcut` function will propagate.

    Prints:
        A message indicating the deletion of each shortcut.
    """
    delete_shortcut('Wizard')
    delete_shortcut('PyWizard')
    delete_shortcut('Server')
    delete_shortcut('Create Repository')
    delete_shortcut('Change Repository')


def create_shortcut(name, exe):
    """
    Creates a desktop shortcut for a specified executable.

    Args:
        name (str): The name of the shortcut to be created.
        exe (str): The name of the executable file for which the shortcut is created.

    This function performs the following steps:
    1. Retrieves the installation directory and desktop path.
    2. Constructs the full path to the shortcut and the target executable.
    3. Sets the working directory and icon location to the installation directory.
    4. Uses the Windows Script Host (WSH) to create and save the shortcut.

    Note:
        - Ensure that the `winshell` and `Dispatch` modules are available.
        - The function assumes the executable exists in the installation directory.

    Prints:
        A message indicating the creation of the shortcut.
    """
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
    """
    Deletes a shortcut file from the desktop.

    Args:
        name (str): The name of the shortcut (without the .lnk extension).

    Behavior:
        - Constructs the full path to the shortcut file on the desktop.
        - Checks if the shortcut file exists.
        - If the file exists, deletes it and prints a confirmation message.

    Note:
        This function assumes that the `winshell` module is installed and 
        accessible, and that the desktop path can be retrieved using `winshell.desktop()`.
    """
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    if os.path.isfile(path):
        os.remove(path)
        print(f"{name} shortcut deleted")


def get_current_install():
    """
    Checks the current installation status of the Wizard application.
    This function verifies the presence of the application in the Windows registry
    and checks if the installation directory exists on the filesystem.
    Returns:
        tuple: A tuple containing:
            - is_reg (bool or None): True if the application is found in the Windows registry, 
              None otherwise.
            - version (str or None): The version of the application retrieved from the registry, 
              or None if not found.
            - is_files (bool or None): True if the installation directory exists, 
              None otherwise.
    """
    is_reg = None
    version = None
    is_files = None

    KEY = "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Wizard"
    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, KEY, 0, winreg.KEY_READ)
        is_reg = True
        version = winreg.QueryValueEx(registry_key, 'DisplayVersion')[0]
        winreg.CloseKey(registry_key)
    except FileNotFoundError:
        pass
    if os.path.isdir(get_install_dir()):
        is_files = True
    return is_reg, version, is_files


def install():
    """
    Installs the Wizard application with elevated privileges.

    This function checks if the script is running with administrative privileges.
    If not, it restarts itself with elevated privileges. Once running as an
    administrator, it performs the following installation steps:
    - Unpacks the necessary files from a ZIP archive.
    - Creates required registry keys.
    - Creates shortcuts for the application.

    Note:
        This function assumes the presence of helper functions:
        - `is_admin()`: Checks if the script is running with admin privileges.
        - `unpack_zip()`: Handles unpacking of the ZIP archive.
        - `create_reg_keys()`: Creates necessary registry keys.
        - `create_shortcuts()`: Creates shortcuts for the application.

    Raises:
        Any exceptions raised by the helper functions during the installation process.
    """
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print(f"Installing...")
        unpack_zip()
        create_reg_keys()
        create_shortcuts()
        print(f"Wizard installed")


def uninstall():
    """
    Uninstalls the Wizard application with elevated privileges.

    This function checks if the script is running with administrative privileges.
    If not, it restarts itself with elevated privileges. Once running as an
    administrator, it performs the following uninstallation steps:
    - Removes the installation directory and its contents.
    - Deletes the registry keys associated with the application.
    - Deletes any shortcuts created for the application.

    Note:
        This function assumes the presence of helper functions:
        - `is_admin()`: Checks if the script is running with admin privileges.
        - `remove_install_dir()`: Deletes the installation directory.
        - `delete_reg_keys()`: Removes registry keys.
        - `delete_shortcuts()`: Deletes application shortcuts.

    Raises:
        Any exceptions raised by the helper functions during the uninstallation process.
    """
    if not is_admin():
        # Restart the script with elevated privileges if not already running as admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print(f"Uninstalling...")
        # Remove the installation directory
        remove_install_dir()
        # Delete registry keys
        delete_reg_keys()
        # Delete application shortcuts
        delete_shortcuts()
        print(f"Wizard uninstalled")


def update():
    """
    Updates the application by first checking for administrative privileges.

    If the current user does not have administrative privileges, the function
    attempts to restart the script with elevated permissions. If the script is
    already running with administrative privileges, it proceeds to uninstall
    the current version of the application and then installs the updated version.

    Steps:
    1. Check if the user has administrative privileges using `is_admin()`.
    2. If not an admin, relaunch the script with elevated permissions using 
       `ctypes.windll.shell32.ShellExecuteW`.
    3. If already an admin, call `uninstall()` to remove the current version.
    4. Call `install()` to install the updated version.

    Note:
    - This function is designed for Windows systems and relies on the `ctypes` 
      library for privilege elevation.
    - Ensure that `is_admin()`, `uninstall()`, and `install()` are implemented 
      elsewhere in the script.

    Raises:
    - Any exceptions raised by `ctypes`, `uninstall()`, or `install()` will 
      propagate to the caller.
    """
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        uninstall()
        install()


class installer(QtWidgets.QWidget):
    """
    A Qt-based GUI class for managing the installation process of the Wizard application.
    This class provides a graphical interface for installing, updating, or removing the Wizard application.
    It includes progress tracking, error handling, and user interaction elements.
    Attributes:
        main_layout (QtWidgets.QVBoxLayout): The main layout of the installer window.
        datas_widget (QtWidgets.QWidget): A widget containing the image and information layout.
        datas_layout (QtWidgets.QHBoxLayout): The layout for the `datas_widget`.
        image_label (QtWidgets.QLabel): A label displaying the Wizard setup icon.
        infos_widget (QtWidgets.QWidget): A widget containing the information labels.
        infos_layout (QtWidgets.QVBoxLayout): The layout for the `infos_widget`.
        infos_label (QtWidgets.QLabel): A label displaying the main information text.
        version_label (QtWidgets.QLabel): A label displaying the version information of the Wizard.
        error_label (QtWidgets.QLabel): A label displaying error messages, if any.
        install_button (QtWidgets.QPushButton): A button to start the installation process.
        progress_bar (QtWidgets.QProgressBar): A progress bar to indicate the installation progress.
        close_button (QtWidgets.QPushButton): A button to close the installer window.
    Methods:
        __init__(parent=None):
            Initializes the installer class and sets up the UI and connections.
        showEvent(event):
            Centers the installer window on the primary screen when shown.
        connect_functions():
            Connects the UI buttons to their respective functions.
        is_done():
            Updates the UI to indicate successful installation.
        is_error(error):
            Updates the UI to indicate an error during the installation process.
        startup():
            Initializes the installer with version information and default messages.
        process():
            Handles the installation process, including updating, removing, or installing the Wizard application.
        build_ui():
            Constructs the user interface for the installer window.
    """

    def __init__(self, parent=None):
        super(installer, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources_path(
            'ressources/icons/wizard_setup.png')))
        self.setWindowTitle(f"Wizard installer")
        self.build_ui()
        self.connect_functions()
        self.startup()

    def showEvent(self, event):
        desktop = QtGui.QGuiApplication.primaryScreen()
        screenRect = desktop.geometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move(int((screen_maxX-self.width())/2),
                  int((screen_maxY-self.height())/2))

    def connect_functions(self):
        self.install_button.clicked.connect(self.process)
        self.close_button.clicked.connect(self.close)

    def is_done(self):
        self.infos_label.setText('Successfully installed !')
        self.progress_bar.setVisible(0)
        self.close_button.setVisible(1)

    def is_error(self, error):
        self.infos_label.setText('An error occured')
        self.progress_bar.setVisible(0)
        self.error_label.setVisible(1)
        self.close_button.setVisible(1)
        self.error_label.setText(error)

    def startup(self):
        version_dic = get_version()
        day = time.strftime('%Y-%m-%d', time.localtime(version_dic['date']))
        version = f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}.{str(version_dic['builds']).zfill(4)} ( {day} )"
        self.version_label.setText(version)
        self.infos_label.setText('Install Wizard ?')

    def process(self):
        self.install_button.setVisible(0)
        self.progress_bar.setVisible(1)
        QtWidgets.QApplication.processEvents()
        try:
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
            self.is_done()
        except:
            self.is_error(str(traceback.format_exc()))

    def build_ui(self):
        self.setFixedWidth(800)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.main_layout.setSpacing(20)
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

        self.infos_label = QtWidgets.QLabel()
        self.infos_label.setObjectName('title_label_2')
        self.infos_layout.addWidget(self.infos_label)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setStyleSheet('color:gray;')
        self.infos_layout.addWidget(self.version_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

        self.error_label = QtWidgets.QLabel()
        self.error_label.setStyleSheet('color:#f0605b;')
        self.main_layout.addWidget(self.error_label)
        self.error_label.setVisible(0)

        self.install_button = QtWidgets.QPushButton('Install')
        self.install_button.setObjectName('blue_button')
        self.main_layout.addWidget(self.install_button)
        self.install_button.setVisible(1)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setVisible(0)
        self.main_layout.addWidget(self.progress_bar)

        self.close_button = QtWidgets.QPushButton('Close')
        self.close_button.setObjectName('blue_button')
        self.main_layout.addWidget(self.close_button)
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
    The main entry point for the Wizard installer application.

    This function performs the following steps:
    1. Checks if the script is running with administrative privileges using `is_admin()`.
    2. If running as an administrator:
        - Sets an environment variable to adjust the screen scaling factor for Qt.
        - Initializes a Qt application with a custom stylesheet.
        - Creates and displays the installer widget.
        - Processes Qt events and starts the application event loop.
    3. If not running as an administrator:
        - Restarts the script with elevated privileges using `ctypes.windll.shell32.ShellExecuteW`.

    Note:
        - This function is specific to Windows systems and relies on the `ctypes` library
          for privilege elevation.
        - Ensure that the `is_admin()` function is implemented and correctly determines
          administrative privileges.

    Raises:
        Any exceptions raised during the execution of the Qt application or privilege
        elevation will propagate to the caller.
    """
    if is_admin():
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0.75"
        app = QtWidgets.QApplication(sys.argv)
        app.setStyleSheet(stylesheet)
        installer_widget = installer()
        installer_widget.show()
        QtWidgets.QApplication.processEvents()
        sys.exit(app.exec())
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)


if __name__ == '__main__':
    main()
