# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
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

class launcher_widget(QtWidgets.QFrame):

    work_env_changed_signal = pyqtSignal(object)

    def __init__(self, parent = None):
        super(launcher_widget, self).__init__(parent)
        
        self.stage_id = None
        self.stage_row = None
        self.variant_row = None
        self.work_env_row = None
        self.version_row = None

        self.refresh_variant_changed = None
        self.update_state = None
        self.refresh_work_env_changed = None
        self.refresh_version_changed = None

        self.build_ui()
        self.connect_functions()
        self.change_stage(None)
        self.update_state_comboBox_style()

    def change_stage(self, stage_id):
        self.stage_id = stage_id
        self.refresh_variants_hard()

    def refresh(self):
        self.refresh_variants()
        self.refresh_state()
        self.refresh_versions()
        self.refresh_infos()

    def refresh_variants(self):
        if self.stage_id is not None:
            self.stage_row = project.get_stage_data(self.stage_id)
        else:
            self.stage_row = None
        if self.stage_row is not None:
            variant_rows = project.get_stage_childs(self.stage_row['id'])
            if variant_rows is not None:
                all_items = [self.variant_comboBox.itemText(i) for i in range(self.variant_comboBox.count())]
                for variant_row in variant_rows:
                    if variant_row['name'] not in all_items:
                        self.variant_comboBox.addItem(variant_row['name'])

    def refresh_variants_hard(self):
        if self.stage_id is not None:
            self.stage_row = project.get_stage_data(self.stage_id)
        else:
            self.stage_row = None
        self.variant_comboBox.clear()
        self.refresh_variant_changed = None

        if self.stage_row is not None:
            variant_rows = project.get_stage_childs(self.stage_row['id'])
            if variant_rows is not None:
                for variant_row in variant_rows:
                    self.variant_comboBox.addItem(variant_row['name'])
                default_variant_name = project.get_variant_data(self.stage_row['default_variant_id'], 'name')
                self.variant_comboBox.setCurrentText(default_variant_name)
        
        self.refresh_variant_changed = 1
        self.variant_changed(by_user=None)

    def variant_changed(self, by_user=1):
        if self.refresh_variant_changed:
            self.variant_row = None
            if self.stage_row is not None:
                self.variant_row = project.get_variant_by_name(self.stage_row['id'],
                                                                self.variant_comboBox.currentText())

                if by_user:
                    if self.variant_row is not None:
                        project.set_stage_default_variant(self.stage_row['id'], self.variant_row['id'])

        self.refresh_state()
        self.refresh_work_envs_hard()

    def refresh_state(self):
        self.update_state = None
        self.state_comboBox.setCurrentText('todo')

        if self.variant_row is not None:
            self.state_comboBox.setCurrentText(self.variant_row['state'])

        self.update_state = 1

    def refresh_work_envs_hard(self):
        self.work_env_comboBox.clear()
        self.refresh_work_env_changed = None

        if self.variant_row is not None:
            self.variant_row = project.get_variant_data(self.variant_row['id'])
            for software_name in assets_vars._stage_softwares_rules_dic_[self.stage_row['name']]:
                    icon = QtGui.QIcon(ressources._sofwares_icons_dic_[software_name])
                    self.work_env_comboBox.addItem(icon, software_name)

            if self.variant_row['default_work_env_id'] is not None:
                default_work_env_name = project.get_work_env_data(self.variant_row['default_work_env_id'], 'name')
                self.work_env_comboBox.setCurrentText(default_work_env_name)

        self.refresh_work_env_changed = 1
        self.work_env_changed(by_user=None)

    def work_env_changed(self, by_user=1):
        if self.refresh_work_env_changed:
            self.work_env_row = None
            if self.variant_row is not None:
                self.work_env_row = project.get_work_env_by_name(self.variant_row['id'],
                                                                self.work_env_comboBox.currentText())

                if by_user:
                    if self.work_env_row is not None:
                        project.set_variant_data(self.variant_row['id'], 'default_work_env_id', self.work_env_row['id'])
                
        self.refresh_versions_hard()

    def refresh_versions(self):
        if self.work_env_row is not None:
            version_rows = project.get_work_versions(self.work_env_row['id'])
            if version_rows is not None:
                all_items = [self.version_comboBox.itemText(i) for i in range(self.version_comboBox.count())]
                for version_row in version_rows:
                    if version_row['name'] not in all_items:
                        self.version_comboBox.addItem(version_row['name'])

    def refresh_versions_hard(self):
        self.version_comboBox.clear()
        self.refresh_version_changed = None

        if self.work_env_row is not None:
            self.work_env_changed_signal.emit(self.work_env_row['id'])
            version_rows = project.get_work_versions(self.work_env_row['id'])
            for version_row in version_rows:
                self.version_comboBox.addItem(version_row['name'])

            self.version_comboBox.setCurrentText(version_rows[-1]['name'])

        elif self.work_env_row == None and self.variant_row is not None:
            self.version_comboBox.addItem('0001')
            self.work_env_changed_signal.emit(None)

        self.refresh_version_changed = 1
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
        else:
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
        self.lock_button.setStyleSheet('')
        self.lock_button.setIcon(QtGui.QIcon(ressources._lock_icons_[0]))
        if self.work_env_row is not None:
            lock_id = project.get_work_env_data(self.work_env_row['id'], 'lock_id')
            if lock_id is not None:
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
        if self.variant_row is not None:
            if self.work_env_row is not None:
                launch.launch_work_version(self.version_row['id'])
                self.refresh()
            else:
                software_name = self.work_env_comboBox.currentText()
                software_id = project.get_software_data_by_name(software_name, 'id')
                work_env_id = assets.create_work_env(software_id, self.variant_row['id'])
                project.set_variant_data(self.variant_row['id'], 'default_work_env_id', work_env_id)
                self.refresh()
                self.launch()

    def state_changed(self, state):
        if self.update_state:
            if self.variant_row is not None:
                project.set_variant_data(self.variant_row['id'], 'state', state)
        self.update_state_comboBox_style()

    def update_state_comboBox_style(self):
        current_state = self.state_comboBox.currentText()
        if current_state == 'todo':
            color = '#a8a8a8'
            hover_color = '#bfbfbf'
        elif current_state == 'wip':
            color = '#f79360'
            hover_color = '#fca97e'
        elif current_state == 'done':
            color = '#98d47f'
            hover_color = '#abe094'
        elif current_state == 'error':
            color = '#f0605b'
            hover_color = '#f0817d'

        css = "QComboBox{font:bold;background-color:%s;}"%color
        css += "QComboBox::drop-down::hover{background-color:%s;}"%hover_color
        self.state_comboBox.setStyleSheet(css)

    def create_variant(self):
        if self.stage_row is not None:
            self.variant_creation_widget = variant_creation_widget(self)
            if self.variant_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                variant_name = self.variant_creation_widget.name_field.text()
                new_variant_id = assets.create_variant(variant_name, self.stage_row['id'])
                project.set_stage_default_variant(self.stage_row['id'], new_variant_id)
                self.refresh_variants_hard()

    def connect_functions(self):
        self.state_comboBox.currentTextChanged.connect(self.state_changed)
        self.variant_comboBox.currentTextChanged.connect(self.variant_changed)
        self.work_env_comboBox.currentTextChanged.connect(self.work_env_changed)
        self.version_comboBox.currentTextChanged.connect(self.version_changed)
        self.launch_button.clicked.connect(self.launch)
        self.lock_button.clicked.connect(self.toggle_lock)
        self.add_variant_button.clicked.connect(self.create_variant)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
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
        self.state_comboBox.addItem('todo')
        self.state_comboBox.addItem('wip')
        self.state_comboBox.addItem('done')
        self.state_comboBox.addItem('error')
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

        self.comment_label = QtWidgets.QLabel()
        self.comment_label.setWordWrap(True)
        self.main_layout.addWidget(self.comment_label)

        self.version_infos_widget = QtWidgets.QWidget()
        self.version_infos_layout = QtWidgets.QHBoxLayout()
        self.version_infos_layout.setContentsMargins(0,0,0,0)
        self.version_infos_layout.setSpacing(6)
        self.version_infos_widget.setLayout(self.version_infos_layout)
        self.main_layout.addWidget(self.version_infos_widget)

        self.date_label = QtWidgets.QLabel()
        self.date_label.setObjectName('gray_label')
        self.version_infos_layout.addWidget(self.date_label)

        self.user_label = QtWidgets.QLabel()
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
