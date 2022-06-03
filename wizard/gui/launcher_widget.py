# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os
import time

# Wizard modules
from wizard.vars import assets_vars
from wizard.vars import ressources
from wizard.core import environment
from wizard.core import assets
from wizard.core import project
from wizard.core import image
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import launch

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import image_viewer_widget

class launcher_widget(QtWidgets.QFrame):

    work_env_changed_signal = pyqtSignal(object)
    variant_changed_signal = pyqtSignal(object)

    def __init__(self, parent = None):
        super(launcher_widget, self).__init__(parent)
        
        self.work_env_id = None
        self.version_row = None
        self.refresh_version_changed = None

        self.build_ui()
        self.connect_functions()
        self.change_work_env(None)

    def change_work_env(self, work_env_id):
        start_time = time.time()
        self.work_env_id = work_env_id
        self.refresh_versions_hard()

    def refresh(self):
        self.refresh_versions()
        if self.version_row is not None:
            self.version_row = project.get_version_data(self.version_row['id'])
        self.refresh_infos()

    def focus_version(self, version_name):
        if version_name in self.versions.keys():
            self.version_comboBox.setCurrentText(version_name)

    def refresh_versions(self, set_last=None):
        if self.work_env_id:
            version_rows = project.get_work_versions(self.work_env_id)
            versions_names = []
            if (version_rows is not None) and (version_rows != []):
                new=0
                for version_row in version_rows:
                    versions_names.append(version_row['name'])
                    if version_row['name'] not in self.versions.keys():
                        self.version_comboBox.addItem(version_row['name'])
                        self.versions[version_row['name']] = version_row['id']
                        new=1

                current_version = self.version_comboBox.currentText()
                combobox_all_items = [self.version_comboBox.itemText(i) for i in range(self.version_comboBox.count())]
                for version_name in combobox_all_items:
                    if version_name not in versions_names:
                        version_index = self.version_comboBox.findData(version_name)
                        self.version_comboBox.removeItem(version_index)
                        if version_name == current_version:
                            set_last = True

                if new or set_last:
                    self.version_comboBox.setCurrentText(version_rows[-1]['name'])
                    self.version_row = version_rows[-1]

        self.refresh_version_changed = True

    def refresh_versions_hard(self):
        self.refresh_version_changed = None
        self.versions = dict()
        self.version_comboBox.clear()
        self.refresh_versions()
        self.version_changed()

    def version_changed(self):
        if self.refresh_version_changed:
            self.version_row = None
            if self.work_env_id:
                self.version_row = project.get_work_version_by_name(self.work_env_id, 
                                                                    self.version_comboBox.currentText())
            self.refresh_infos()

    def refresh_infos(self):
        if self.version_row:
            self.user_label.setText(self.version_row['creation_user'])
            if self.version_row['comment'] != '':
                self.comment_label.setText(self.version_row['comment'])
            else:
                self.comment_label.setText('Missing comment')
            day, hour = tools.convert_time(self.version_row['creation_time'])
            self.date_label.setText(f"{day} - {hour}")
            self.refresh_screenshot(self.version_row['screenshot_path'])
            self.refresh_lock_button()
            self.refresh_launch_button()
        else:
            self.user_label.setText('user')
            self.comment_label.setText('comment')
            self.date_label.setText('date')
            self.refresh_screenshot('')
            self.refresh_lock_button()
            self.refresh_launch_button()

    def refresh_launch_button(self):
        if self.work_env_id:
            if self.work_env_id in launch.get():
                self.launch_button.start_animation()
                self.show_kill_button()
            else:
                self.launch_button.stop_animation()
                self.hide_kill_button()
        else:
            self.launch_button.stop_animation()
            self.hide_kill_button()

    def refresh_screenshot(self, screenshot_path):
        if path_utils.isfile(screenshot_path):
            image_bytes, width, height = image.convert_screenshot(screenshot_path)
            self.screenshot_button.setFixedSize(width, height)
            pm = gui_utils.round_corners_image_button(image_bytes, (width, height), 10)
            icon = QtGui.QIcon()
            icon.addPixmap(pm)
            self.screenshot_button.setIcon(icon)
        else:
            screenshot_path = ressources._no_screenshot_
            self.screenshot_button.setFixedSize(300, 169)
            self.screenshot_button.setIcon(QtGui.QIcon(screenshot_path))

    def refresh_lock_button(self):
        self.lock_button.setStyleSheet('')
        gui_utils.modify_application_tooltip(self.lock_button, "Lock work environment")
        self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[0]))
        if self.work_env_id:
            lock_id = project.get_work_env_data(self.work_env_id, 'lock_id')
            if lock_id is not None:
                gui_utils.modify_application_tooltip(self.lock_button, "Unlock work environment")
                css = "QPushButton{border: 2px solid #f0605b;background-color: #f0605b;}"
                css += "QPushButton::hover{border: 2px solid #ff817d;background-color: #ff817d;}"
                css += "QPushButton::pressed{border: 2px solid #ab4946;background-color: #ab4946;}"
                self.lock_button.setStyleSheet(css)
                self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[1]))

    def toggle_lock(self):
        if self.work_env_id:
            project.toggle_lock(self.work_env_id)
            gui_server.refresh_team_ui()

    def launch(self):
        if self.work_env_id:
            launch.launch_work_version(self.version_row['id'])
            gui_server.refresh_team_ui()

    def connect_functions(self):
        self.version_comboBox.currentTextChanged.connect(self.version_changed)
        self.launch_button.clicked.connect(self.launch)
        self.lock_button.clicked.connect(self.toggle_lock)
        self.screenshot_button.clicked.connect(self.show_screen_shot)
        self.kill_button.clicked.connect(self.kill)

    def kill(self):
        if self.work_env_id:
            launch.kill(self.work_env_id)
            gui_server.refresh_team_ui()

    def show_screen_shot(self):
        if self.version_row is not None:
            screenshot_path = self.version_row['screenshot_path']
            if path_utils.isfile(screenshot_path):
                self.image_viewer_widget = image_viewer_widget.image_viewer_widget(screenshot_path)
                self.image_viewer_widget.show()

    def show_kill_button(self):
        if not self.kill_button.isVisible():
            self.kill_button.setMaximumWidth(60)
            self.kill_button.setMinimumWidth(0)
            self.kill_button.setVisible(1)
            self.anim = QtCore.QPropertyAnimation(self.kill_button, b"maximumWidth")
            self.anim.setDuration(100)
            self.anim.setStartValue(0)
            self.anim.setEndValue(60)
            self.anim.start()

    def hide_kill_button(self):
        if self.kill_button.isVisible():
            self.kill_button.setMaximumWidth(60)
            self.kill_button.setMinimumWidth(0)
            self.anim = QtCore.QPropertyAnimation(self.kill_button, b"maximumWidth")
            self.anim.setDuration(100)
            self.anim.setStartValue(60)
            self.anim.setEndValue(0)
            self.anim.finished.connect(lambda:self.kill_button.setVisible(0))
            self.anim.start()

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.screenshot_button = QtWidgets.QPushButton()
        self.screenshot_button.setObjectName('screenshot_button')
        gui_utils.application_tooltip(self.screenshot_button, "Show version screenshot")
        self.screenshot_button.setFixedWidth(300)
        self.screenshot_button.setIconSize(QtCore.QSize(298, 298))
        self.main_layout.addWidget(self.screenshot_button)

        self.version_comboBox = gui_utils.QComboBox()
        gui_utils.application_tooltip(self.version_comboBox, "Change version")
        self.main_layout.addWidget(self.version_comboBox)

        self.comment_label = QtWidgets.QLabel('comment')
        gui_utils.application_tooltip(self.comment_label, "Version comment")
        self.comment_label.setWordWrap(True)
        self.main_layout.addWidget(self.comment_label)

        self.version_infos_widget = QtWidgets.QWidget()
        self.version_infos_layout = QtWidgets.QHBoxLayout()
        self.version_infos_layout.setContentsMargins(0,0,0,0)
        self.version_infos_layout.setSpacing(6)
        self.version_infos_widget.setLayout(self.version_infos_layout)
        self.main_layout.addWidget(self.version_infos_widget)

        self.date_label = QtWidgets.QLabel('date')
        gui_utils.application_tooltip(self.date_label, "Version date")
        self.date_label.setObjectName('gray_label')
        self.version_infos_layout.addWidget(self.date_label)

        self.user_label = QtWidgets.QLabel('user')
        gui_utils.application_tooltip(self.user_label, "Version user")
        self.version_infos_layout.addWidget(self.user_label)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.version_infos_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.lock_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.lock_button, "Lock work environment")
        self.lock_button.setFixedSize(60,60)
        self.lock_button.setIconSize(QtCore.QSize(25,25))
        self.buttons_layout.addWidget(self.lock_button)

        self.launch_button = custom_launchButton('Launch')
        gui_utils.application_tooltip(self.launch_button, "Launch work version")
        self.launch_button.setMinimumHeight(60)
        self.launch_button.setObjectName('blue_button')
        self.launch_button.setStyleSheet('font:bold')
        self.buttons_layout.addWidget(self.launch_button)

        self.kill_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.kill_button, "Kill work environment")
        self.kill_button.setFixedSize(0,60)
        self.kill_button.setVisible(0)
        self.kill_button.setIconSize(QtCore.QSize(25,25))
        self.kill_button.setIcon(QtGui.QIcon(ressources._kill_task_icon_))
        self.buttons_layout.addWidget(self.kill_button)

class custom_launchButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(custom_launchButton, self).__init__(parent)
        self.setIcon(QtGui.QIcon())
        self.setIconSize(QtCore.QSize(25,25))
        self.animated_spinner = QtGui.QMovie(ressources._running_gif_)
        self.animated_spinner.frameChanged.connect(self.updateSpinnerAnimation)           

    def updateSpinnerAnimation(self):
        self.setIcon(QtGui.QIcon(self.animated_spinner.currentPixmap()))

    def start_animation(self):
        self.setText('    Running')
        self.animated_spinner.start()

    def stop_animation(self):
        self.setText('Launch')
        self.animated_spinner.stop()
        self.setIcon(QtGui.QIcon())
