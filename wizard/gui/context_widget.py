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
from wizard.core import path_utils

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

class context_widget(QtWidgets.QFrame):

    work_env_changed_signal = pyqtSignal(object)
    variant_changed_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(context_widget, self).__init__(parent)

        self.stage_id = None
        self.stage_row = None
        self.variant_row = None

        self.refresh_variant_changed = None
        self.refresh_work_env_changed = None

        self.build_ui()
        self.connect_functions()
        self.change_stage(None)

    def refresh(self):
        self.refresh_variants()

    def change_stage(self, stage_id):
        self.stage_id = stage_id
        self.refresh_variants_hard()

    def focus_variant(self, variant_id):
        self.refresh_variant_changed = None
        variant_row = project.get_variant_data(variant_id)
        if variant_row is not None:
            if variant_row['name'] in self.variants.keys():
                self.variant_comboBox.setCurrentText(variant_row['name'])
        self.refresh_variant_changed = 1
        self.variant_changed(by_user=None)

    def focus_work_env(self, work_env_id):
        self.refresh_work_env_changed = None
        work_env_row = project.get_work_env_data(work_env_id)
        if work_env_row is not None:
            self.work_env_comboBox.setCurrentText(work_env_row['name'])
        self.refresh_work_env_changed = 1
        self.work_env_changed(by_user=None)

    def refresh_variants(self, apply_default=None):
        self.refresh_variant_changed = None
        if self.stage_id is not None:
            self.stage_row = project.get_stage_data(self.stage_id)
        else:
            self.stage_row = None
        if self.stage_row is not None:
            variant_rows = project.get_stage_childs(self.stage_row['id'])
            if variant_rows is not None:
                for variant_row in variant_rows:
                    if variant_row['name'] not in self.variants.keys():
                        self.variant_comboBox.addItem(variant_row['name'])
                        self.variants[variant_row['name']] = variant_row['id']
            if apply_default:
                default_variant_name = project.get_variant_data(self.stage_row['default_variant_id'], 'name')
                self.variant_comboBox.setCurrentText(default_variant_name)
        self.refresh_variant_changed = 1

    def refresh_variants_hard(self):
        self.refresh_variant_changed = None
        self.variants = dict()
        self.variant_comboBox.clear()
        self.refresh_variants(apply_default=1)
        self.variant_changed(by_user=None)

    def variant_changed(self, by_user=1):
        if self.refresh_variant_changed:
            self.variant_row = None
            if self.stage_row is not None:
                self.variant_row = project.get_variant_by_name(self.stage_id, self.variant_comboBox.currentText())
            self.refresh_work_envs_hard()

            if self.variant_row is not None:
                if by_user:
                    project.set_stage_default_variant(self.stage_row['id'], self.variant_row['id'])
                self.variant_changed_signal.emit(self.variant_row['id'])
            else:
                self.variant_changed_signal.emit(None)

    def refresh_work_envs_hard(self):
        self.refresh_work_env_changed = None
        self.work_env_comboBox.clear()

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

                if self.work_env_row is not None and self.variant_row is not None:
                    self.work_env_changed_signal.emit(self.work_env_row['id'])
                    self.hide_init_work_env_button()
                elif self.work_env_row == None and self.variant_row is not None:
                    self.work_env_changed_signal.emit(None)
                    self.show_init_work_env_button()
            else:
                self.work_env_changed_signal.emit(0)
                self.hide_init_work_env_button()
            self.refresh_string_asset_label()
            self.refresh_extension_hard()

    def refresh_extension_hard(self):
        self.refresh_extension_changed = None
        self.export_extension_comboBox.clear()

        if self.stage_row is not None and self.work_env_row is not None:
            extensions_list = assets_vars._ext_dic_[self.stage_row['name']][self.work_env_row['name']]
            if self.stage_row['name'] != assets_vars._custom_stage_:
                default_extension = f"Default ({project.get_default_extension(self.stage_row['name'], self.work_env_row['software_id'])})"
                extensions_list = [default_extension] + extensions_list
            self.export_extension_comboBox.addItems(extensions_list)

            if self.work_env_row['export_extension'] is None:
                self.export_extension_comboBox.setCurrentText(default_extension)
            else:
                self.export_extension_comboBox.setCurrentText(self.work_env_row['export_extension'])

        self.refresh_extension_changed = 1

    def extension_changed(self):
        if self.refresh_extension_changed:
            export_extension = self.export_extension_comboBox.currentText()
            if 'Default' in export_extension:
                export_extension = None
            project.set_work_env_extension(self.work_env_row['id'], export_extension)

    def connect_functions(self):
        self.variant_comboBox.currentTextChanged.connect(self.variant_changed)
        self.work_env_comboBox.currentTextChanged.connect(self.work_env_changed)
        self.export_extension_comboBox.currentTextChanged.connect(self.extension_changed)
        self.add_variant_button.clicked.connect(self.create_variant)
        self.folder_button.clicked.connect(self.open_work_env_folder)
        self.sandbox_button.clicked.connect(self.open_sandbox_folder)
        self.init_work_env_button.clicked.connect(self.init_work_env)

    def refresh_string_asset_label(self):
        if self.work_env_row is not None and self.variant_row is not None:
            string_asset = assets.instance_to_string(('work_env', self.work_env_row['id']))
            self.string_asset_label.setText(string_asset)
        else:
            self.string_asset_label.setText('')

    def open_work_env_folder(self):
        if self.work_env_row is not None and self.variant_row is not None:
            work_env_path = assets.get_work_env_path(self.work_env_row['id'])
            if path_utils.isdir(work_env_path):
                path_utils.startfile(work_env_path)

    def open_sandbox_folder(self):
        if self.variant_row is not None:
            sandbox_path = path_utils.join(assets.get_variant_path(self.variant_row['id']), '_SANDBOX')
            if path_utils.isdir(sandbox_path):
                path_utils.startfile(sandbox_path)

    def create_variant(self):
        if self.stage_row is not None:
            self.variant_creation_widget = variant_creation_widget(self)
            if self.variant_creation_widget.exec_() == QtWidgets.QDialog.Accepted:
                variant_name = self.variant_creation_widget.name_field.text()
                new_variant_id = assets.create_variant(variant_name, self.stage_row['id'])
                if new_variant_id:
                    project.set_stage_default_variant(self.stage_row['id'], new_variant_id)
                    gui_server.refresh_team_ui()

    def init_work_env(self):
        if self.work_env_row is None:
            software_name = self.work_env_comboBox.currentText()
            software_id = project.get_software_data_by_name(software_name, 'id')
            work_env_id = assets.create_work_env(software_id, self.variant_row['id'])
            project.set_variant_data(self.variant_row['id'], 'default_work_env_id', work_env_id)
            self.refresh_work_envs_hard()
            gui_server.refresh_team_ui()

    def show_init_work_env_button(self):
        if not self.init_work_env_button.isVisible():
            self.init_work_env_button.setMaximumWidth(200)
            self.init_work_env_button.setMinimumWidth(0)
            self.init_work_env_button.setVisible(1)
            self.anim = QtCore.QPropertyAnimation(self.init_work_env_button, b"maximumWidth")
            self.anim.setDuration(100)
            self.anim.setStartValue(0)
            self.anim.setEndValue(200)
            self.anim.start()

    def hide_init_work_env_button(self):
        if self.init_work_env_button.isVisible():
            self.init_work_env_button.setMaximumWidth(200)
            self.init_work_env_button.setMinimumWidth(0)
            self.anim = QtCore.QPropertyAnimation(self.init_work_env_button, b"maximumWidth")
            self.anim.setDuration(100)
            self.anim.setStartValue(200)
            self.anim.setEndValue(0)
            self.anim.finished.connect(lambda:self.init_work_env_button.setVisible(0))
            self.anim.start()

    def build_ui(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(3,3,3,3)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.add_variant_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.add_variant_button, "Create variant")
        self.add_variant_button.setFixedSize(29,29)
        self.add_variant_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.add_variant_button.setIconSize(QtCore.QSize(14,14))
        self.main_layout.addWidget(self.add_variant_button)

        self.variant_comboBox = gui_utils.QComboBox()
        self.variant_comboBox.setFixedWidth(150)
        gui_utils.application_tooltip(self.variant_comboBox, "Change variant")
        self.main_layout.addWidget(self.variant_comboBox)

        self.work_env_comboBox = gui_utils.QComboBox()
        self.work_env_comboBox.setFixedWidth(190)
        gui_utils.application_tooltip(self.work_env_comboBox, "Change work environment")
        self.main_layout.addWidget(self.work_env_comboBox)

        self.init_work_env_button = QtWidgets.QPushButton('Init work environment')
        self.init_work_env_button.setObjectName('init_work_env_button')
        self.init_work_env_button.setFixedHeight(29)
        self.init_work_env_button.setVisible(0)
        gui_utils.application_tooltip(self.init_work_env_button, "Init work environment")
        self.main_layout.addWidget(self.init_work_env_button)

        self.export_extension_comboBox = gui_utils.QComboBox()
        self.export_extension_comboBox.setFixedWidth(150)
        gui_utils.application_tooltip(self.export_extension_comboBox, "Change export extension")
        self.main_layout.addWidget(self.export_extension_comboBox)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.string_asset_label = QtWidgets.QLabel()
        self.string_asset_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.main_layout.addWidget(self.string_asset_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(8,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.folder_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.folder_button, "Open work environment folder")
        self.folder_button.setFixedSize(QtCore.QSize(26, 26))
        self.folder_button.setIconSize(QtCore.QSize(20, 20))
        self.folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.main_layout.addWidget(self.folder_button)

        self.sandbox_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.sandbox_button, "Open sandbox folder")
        self.sandbox_button.setFixedSize(QtCore.QSize(26, 26))
        self.sandbox_button.setIconSize(QtCore.QSize(20, 20))
        self.sandbox_button.setIcon(QtGui.QIcon(ressources._sandbox_icon_))
        self.main_layout.addWidget(self.sandbox_button)

class variant_creation_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(variant_creation_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

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

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_layout.addWidget(QtWidgets.QLabel('New variant'))
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.name_field = QtWidgets.QLineEdit()
        self.frame_layout.addWidget(self.name_field)

        self.accept_button = QtWidgets.QPushButton('Create')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)
        self.close_pushButton.clicked.connect(self.reject)