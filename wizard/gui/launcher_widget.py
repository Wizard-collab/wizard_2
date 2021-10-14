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
        
        self.work_env_row = None
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
        start_time = time.time()
        if self.work_env_row is not None:
            self.work_env_row = project.get_work_env_data(self.work_env_row['id'])
        self.refresh_versions()
        if self.version_row is not None:
            self.version_row = project.get_version_data(self.version_row['id'])
        self.refresh_infos()

    def focus_version(self, version_name):
        if version_name in self.versions.keys():
            self.version_comboBox.setCurrentText(version_name)

    def refresh_versions(self, set_last=None):
        if self.work_env_id is not None:
            self.work_env_row = project.get_work_env_data(self.work_env_id)

        if self.work_env_row is not None and self.work_env_id is not None:
            version_rows = project.get_work_versions(self.work_env_row['id'])
            if (version_rows is not None) and (version_rows != []):
                new=0
                for version_row in version_rows:
                    if version_row['name'] not in self.versions.keys():
                        self.version_comboBox.addItem(version_row['name'])
                        self.versions[version_row['name']] = version_row['id']
                        new=1
                if new or set_last:
                    self.version_comboBox.setCurrentText(version_rows[-1]['name'])
                    self.version_row = version_rows[-1]
        elif self.work_env_row == None and self.work_env_id is not None:
            self.version_comboBox.addItem('0001')
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
            if self.work_env_row is not None:
                self.version_row = project.get_work_version_by_name(self.work_env_row['id'], 
                                                                    self.version_comboBox.currentText())
            self.refresh_infos()

    def refresh_infos(self):
        if self.version_row:
            self.user_label.setText(self.version_row['creation_user'])
            self.comment_label.setText(self.version_row['comment'])
            day, hour = tools.convert_time(self.version_row['creation_time'])
            self.date_label.setText(f"{day} - {hour}")
            self.refresh_screenshot(self.version_row['screenshot_path'])
            self.refresh_lock_button()
            self.refresh_launch_button()
            self.refresh_work_time()
        else:
            self.user_label.setText('')
            self.comment_label.setText('')
            self.work_time_label.setText('')
            self.date_label.setText('')
            self.refresh_screenshot('')
            self.refresh_lock_button()
            self.refresh_launch_button()

    def refresh_work_time(self):
        if self.work_env_row is not None:
            work_hours, work_minutes, work_seconds = tools.convert_seconds(self.work_env_row['work_time'])
            self.work_time_label.setText(f"{work_hours}h:{work_minutes}m:{work_seconds}s")

    def refresh_launch_button(self):
        if self.work_env_row is not None:
            if self.work_env_row['id'] in launch.get():
                self.launch_button.start_animation()
                self.show_kill_button()
            else:
                self.launch_button.stop_animation()
                self.hide_kill_button()
        else:
            self.launch_button.stop_animation()
            self.hide_kill_button()

    def refresh_screenshot(self, screenshot_path):
        if not os.path.isfile(screenshot_path):
            screenshot_path = ressources._no_screenshot_
        image_bytes, width, height = image.convert_screenshot(screenshot_path)
        self.screenshot_button.setFixedSize(width, height)
        gui_utils.round_corners_image_button(self.screenshot_button, image_bytes, (width, height), 10)

    def refresh_lock_button(self):
        self.lock_button.setStyleSheet('')
        gui_utils.modify_application_tooltip(self.lock_button, "Lock work environment")
        self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[0]))
        if self.work_env_row is not None:
            lock_id = project.get_work_env_data(self.work_env_row['id'], 'lock_id')
            if lock_id is not None:
                gui_utils.modify_application_tooltip(self.lock_button, "Unlock work environment")
                css = "QPushButton{border: 2px solid #f0605b;background-color: #f0605b;}"
                css += "QPushButton::hover{border: 2px solid #ff817d;background-color: #ff817d;}"
                css += "QPushButton::pressed{border: 2px solid #ab4946;background-color: #ab4946;}"
                self.lock_button.setStyleSheet(css)
                self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[1]))

    def toggle_lock(self):
        if self.work_env_row is not None:
            project.toggle_lock(self.work_env_row['id'])
            self.refresh_lock_button()

    def launch(self):
        if self.work_env_id is not None:
            if self.work_env_row is not None:
                launch.launch_work_version(self.version_row['id'])
            else:
                software_name = self.work_env_comboBox.currentText()
                software_id = project.get_software_data_by_name(software_name, 'id')
                work_env_id = assets.create_work_env(software_id, self.variant_row['id'])
                project.set_variant_data(self.variant_row['id'], 'default_work_env_id', work_env_id)
                self.refresh_work_envs_hard()
                self.launch()
            gui_server.refresh_ui()

    def connect_functions(self):
        self.version_comboBox.currentTextChanged.connect(self.version_changed)
        self.launch_button.clicked.connect(self.launch)
        self.lock_button.clicked.connect(self.toggle_lock)
        self.screenshot_button.clicked.connect(self.show_screen_shot)
        self.kill_button.clicked.connect(self.kill)

    def kill(self):
        if self.work_env_row is not None:
            launch.kill(self.work_env_row['id'])

    def show_screen_shot(self):
        if self.version_row is not None:
            screenshot_path = self.version_row['screenshot_path']
            if os.path.isfile(screenshot_path):
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
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.screenshot_button = QtWidgets.QPushButton()
        self.screenshot_button.setObjectName('screenshot_button')
        gui_utils.application_tooltip(self.screenshot_button, "Show version screenshot")
        self.screenshot_button.setFixedWidth(300)
        self.screenshot_button.setIconSize(QtCore.QSize(298, 298))
        self.main_layout.addWidget(self.screenshot_button)

        self.version_comboBox = QtWidgets.QComboBox()
        gui_utils.application_tooltip(self.version_comboBox, "Change version")
        self.version_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.main_layout.addWidget(self.version_comboBox)

        self.work_time_label = QtWidgets.QLabel()
        gui_utils.application_tooltip(self.work_time_label, "Work environment work time")
        self.work_time_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.work_time_label)

        self.comment_label = QtWidgets.QLabel()
        gui_utils.application_tooltip(self.comment_label, "Version comment")
        self.comment_label.setWordWrap(True)
        self.main_layout.addWidget(self.comment_label)

        self.version_infos_widget = QtWidgets.QWidget()
        self.version_infos_layout = QtWidgets.QHBoxLayout()
        self.version_infos_layout.setContentsMargins(0,0,0,0)
        self.version_infos_layout.setSpacing(6)
        self.version_infos_widget.setLayout(self.version_infos_layout)
        self.main_layout.addWidget(self.version_infos_widget)

        self.date_label = QtWidgets.QLabel()
        gui_utils.application_tooltip(self.date_label, "Version date")
        self.date_label.setObjectName('gray_label')
        self.version_infos_layout.addWidget(self.date_label)

        self.user_label = QtWidgets.QLabel()
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
        self.kill_button.setIconSize(QtCore.QSize(28,28))
        self.kill_button.setIcon(QtGui.QIcon(ressources._kill_task_icon_))
        self.buttons_layout.addWidget(self.kill_button)

        self.refresh_label = QtWidgets.QLabel()
        self.refresh_label.setAlignment(QtCore.Qt.AlignRight)
        self.refresh_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.refresh_label)

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
