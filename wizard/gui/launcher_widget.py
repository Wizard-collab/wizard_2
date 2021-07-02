# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os

# Wizard modules
from wizard.vars import assets_vars
from wizard.vars import ressources
from wizard.core import assets
from wizard.core import project
from wizard.core import image
from wizard.core import tools
from wizard.core import launch

# Wizard gui modules
from wizard.gui import gui_utils

red_button_css = '''#plain_red_button{
                        border: 2px solid #f0605b;
                        background-color: #f0605b;
                    }

                    #plain_red_button::hover{
                        background-color: #ff817d;
                        border: 2px solid #ff817d;
                    }

                    #plain_red_button::pressed{
                        background-color: #ab4946;
                        border: 2px solid #ab4946;
                    }'''

classic_button_css = '''QPushButton, #classic_button{
                        border: 2px solid #42424d;
                        background-color: #42424d;
                        padding: 12px;
                        border-radius: 5px;
                    }

                    QPushButton::hover, #classic_button::hover{
                        border: 2px solid #4b4b57;
                        background-color: #4b4b57;
                    }

                    QPushButton::pressed, #classic_button::pressed{
                        border: 2px solid #1d1d21;
                        background-color: #1d1d21;
                    }'''

class launcher_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(launcher_widget, self).__init__(parent)
        self.stage_id = None
        self.stage_row = None

        self.update_state = None
        self.update_work_env = None
        self.update_versions = None
        self.update_infos = None

        self.build_ui()
        self.connect_functions()
        self.fill_state_comboBox()

    def refresh(self, stage_id):
        self.stage_id = stage_id
        if self.stage_id is not None:
            self.stage_row = project.get_stage_data(self.stage_id)
        else:
            self.stage_row = None
        self.refresh_variants()

    def refresh_variants(self):
        self.update_state = None
        self.update_work_env = None

        self.variant_comboBox.clear()
        self.variants_dic = dict()

        if self.stage_row is not None:
            self.setEnabled(True)
            variants_rows = project.get_stage_childs(self.stage_id)

            for variant_row in variants_rows:
                self.variants_dic[variant_row['name']] = variant_row['id']
                self.variant_comboBox.addItem(variant_row['name'])

            default_variant_row = project.get_variant_data(self.stage_row['default_variant_id'])
            self.variant_comboBox.setCurrentText(default_variant_row['name'])

        else:
            self.setEnabled(False)
            self.state_comboBox.setCurrentText('todo')

        self.update_work_env = 1
        self.update_state = 1
        self.refresh_work_envs()

    def refresh_work_envs(self):
        if self.update_work_env:
            self.update_versions = None
            self.variant_row = None
            self.work_env_comboBox.clear()
            
            if self.stage_row is not None:

                for software_name in assets_vars._stage_softwares_rules_dic_[self.stage_row['name']]:
                    icon = QtGui.QIcon(ressources._sofwares_icons_dic_[software_name])
                    self.work_env_comboBox.addItem(icon, software_name)

                self.variant_row = project.get_variant_data(self.variants_dic[self.variant_comboBox.currentText()])
                project.set_stage_default_variant(self.stage_id, self.variant_row['id'])

                self.state_comboBox.setCurrentText(self.variant_row['state'])

                if self.variant_row['default_work_env_id'] is not None:
                    default_work_env_name = project.get_work_env_data(self.variant_row['default_work_env_id'], 'name')
                    self.work_env_comboBox.setCurrentText(default_work_env_name)

            self.update_versions = 1
            self.refresh_versions(1)

    def refresh_versions(self, set_last=None):
        if self.update_versions:
            self.update_infos = None
            self.work_env_row = None
            self.version_comboBox.clear()
            self.versions_dic = dict()

            if self.variant_row is not None:
                self.work_env_row = project.get_work_env_by_name(self.variant_row['id'], self.work_env_comboBox.currentText())
                if self.work_env_row is not None:
                    project.set_variant_data(self.variant_row['id'], 'default_work_env_id', self.work_env_row['id'])
                    version_rows = project.get_work_versions(self.work_env_row['id'])
                    for version_row in version_rows:
                        self.versions_dic[version_row['name']] = version_row['id']
                        self.version_comboBox.addItem(version_row['name'])
                    if set_last:
                        self.version_comboBox.setCurrentText(version_rows[-1]['name'])
                else:
                    self.version_comboBox.addItem('0001')

            self.update_infos = 1
            self.refresh_infos()

    def toggle_lock(self):
        if self.work_env_row:
            project.toggle_lock(self.work_env_row['id'])
            self.refresh_infos()

    def refresh_infos(self):
        if self.update_infos:
            if self.work_env_row:
                self.version_id = self.versions_dic[self.version_comboBox.currentText()]
                version_row = project.get_version_data(self.version_id)
                self.user_label.setText(version_row['creation_user'])
                self.comment_label.setText(version_row['comment'])
                day, hour = tools.convert_time(version_row['creation_time'])
                self.date_label.setText(f"{day} - {hour}")
                self.refresh_screenshot(version_row['screenshot_path'])
                self.refresh_lock_button()
            else:
                self.version_id = None
                self.user_label.setText('')
                self.comment_label.setText('')
                self.date_label.setText('')
                self.refresh_screenshot('')
                self.refresh_lock_button()

    def refresh_screenshot(self, screenshot_path):
        if not os.path.isfile(screenshot_path):
            screenshot_path = ressources._no_screenshot_
        image_bytes, width, height = image.convert_screenshot(screenshot_path)
        self.screenshot_label.setFixedSize(width, height)
        gui_utils.round_corners_image(self.screenshot_label, image_bytes, (width, height), 10)

    def refresh_lock_button(self):
        if self.work_env_row is not None:
            lock_id = project.get_work_env_data(self.work_env_row['id'], 'lock_id')
            if lock_id is not None:
                self.lock_button.setObjectName('plain_red_button')
                self.lock_button.setStyleSheet(red_button_css)
                self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[1]))
            else:
                self.lock_button.setObjectName('classic_button')
                self.lock_button.setStyleSheet(classic_button_css)
                self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[0]))
        else:
            self.lock_button.setObjectName('classic_button')
            self.lock_button.setStyleSheet(classic_button_css)
            self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[0]))

    def launch(self):
        if self.variant_row is not None:
            if self.work_env_row is not None:
                version_id = self.versions_dic[self.version_comboBox.currentText()]
                launch.launch_work_version(version_id)
                self.refresh_infos()
            else:
                software_name = self.work_env_comboBox.currentText()
                software_id = project.get_software_data_by_name(software_name, 'id')
                work_env_id = assets.create_work_env(software_id, self.variant_row['id'])
                project.set_variant_data(self.variant_row['id'], 'default_work_env_id', work_env_id)
                self.refresh_work_envs()
                self.launch()

    def fill_state_comboBox(self):
        self.state_comboBox.addItem('todo')
        self.state_comboBox.addItem('wip')
        self.state_comboBox.addItem('done')
        self.state_comboBox.addItem('error')

    def update_variant_state(self, state):
        if self.update_state:
            if self.variant_row is not None:
                project.set_variant_data(self.variant_row['id'], 'state', state)

    def update_state_comboBox_style(self):
        current_state = self.state_comboBox.currentText()
        if current_state == 'todo':
            color = 'gray'
        elif current_state == 'wip':
            color = '#f79360'
        elif current_state == 'done':
            color = '#9cf277'
        elif current_state == 'error':
            color = '#f0605b'
        self.state_comboBox.setStyleSheet(f"background-color:{color};")

    def create_variant(self):
        if self.stage_row is not None:
            self.variant_creation_widget = variant_creation_widget(self)
            if self.variant_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                variant_name = self.variant_creation_widget.name_field.text()
                new_variant_id = assets.create_variant(variant_name, self.stage_id)
                project.set_stage_default_variant(self.stage_id, new_variant_id)
                self.refresh_variants()

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.update_state_comboBox_style)
        self.state_comboBox.currentTextChanged.connect(self.update_variant_state)
        self.variant_comboBox.currentTextChanged.connect(self.refresh_work_envs)
        self.work_env_comboBox.currentTextChanged.connect(self.refresh_versions)
        self.version_comboBox.currentTextChanged.connect(self.refresh_infos)
        self.launch_button.clicked.connect(self.launch)
        self.lock_button.clicked.connect(self.toggle_lock)
        self.add_variant_button.clicked.connect(self.create_variant)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.screenshot_label = QtWidgets.QLabel()
        self.screenshot_label.setFixedWidth(300)
        self.main_layout.addWidget(self.screenshot_label)

        self.variant_widget = QtWidgets.QWidget()
        self.variant_layout = QtWidgets.QHBoxLayout()
        self.variant_layout.setContentsMargins(0,0,0,0)
        self.variant_layout.setSpacing(6)
        self.variant_widget.setLayout(self.variant_layout)
        self.main_layout.addWidget(self.variant_widget)

        self.variant_comboBox = QtWidgets.QComboBox()
        self.variant_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.variant_layout.addWidget(self.variant_comboBox)

        self.state_comboBox = QtWidgets.QComboBox()
        self.state_comboBox.setFixedWidth(80)
        self.state_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.variant_layout.addWidget(self.state_comboBox)

        self.add_variant_button = QtWidgets.QPushButton()
        self.add_variant_button.setFixedSize(29,29)
        self.add_variant_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.add_variant_button.setIconSize(QtCore.QSize(14,14))
        self.variant_layout.addWidget(self.add_variant_button)

        self.work_env_comboBox = QtWidgets.QComboBox()
        self.work_env_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.main_layout.addWidget(self.work_env_comboBox)

        self.version_comboBox = QtWidgets.QComboBox()
        self.version_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.main_layout.addWidget(self.version_comboBox)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.comment_label = QtWidgets.QLabel("Retake mdr lol prout proueozj foezifj eoifjzef")
        self.comment_label.setWordWrap(True)
        self.main_layout.addWidget(self.comment_label)

        self.version_infos_widget = QtWidgets.QWidget()
        self.version_infos_layout = QtWidgets.QHBoxLayout()
        self.version_infos_layout.setContentsMargins(0,0,0,0)
        self.version_infos_layout.setSpacing(6)
        self.version_infos_widget.setLayout(self.version_infos_layout)
        self.main_layout.addWidget(self.version_infos_widget)

        self.date_label = QtWidgets.QLabel('23/06/1995 - 23:15')
        self.date_label.setObjectName('gray_label')
        self.version_infos_layout.addWidget(self.date_label)

        self.user_label = QtWidgets.QLabel('j.smith')
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
        self.lock_button.setFixedSize(60,60)
        self.buttons_layout.addWidget(self.lock_button)

        self.launch_button = QtWidgets.QPushButton('Launch')
        self.launch_button.setMinimumHeight(60)
        self.launch_button.setObjectName('blue_button')
        self.launch_button.setStyleSheet('font:bold')
        self.buttons_layout.addWidget(self.launch_button)

class variant_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(variant_creation_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()
        self.name_field.setFocus()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#variant_creation_widget{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)
        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = QtWidgets.QPushButton()
        self.close_pushButton.setObjectName('close_button')
        self.close_pushButton.setIcon(QtGui.QIcon(ressources._close_icon_))
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.name_field = QtWidgets.QLineEdit()
        self.frame_layout.addWidget(self.name_field)

        self.accept_button = QtWidgets.QPushButton('Create')
        self.accept_button.setObjectName("blue_button")
        self.frame_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)
        self.close_pushButton.clicked.connect(self.reject)
