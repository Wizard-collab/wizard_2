# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import json
import logging

# Wizard modules
from wizard.vars import ressources
from wizard.vars import assets_vars
from wizard.core import project

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)

class export_preferences_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(export_preferences_widget, self).__init__(parent)

        self.combobox_list = []

        self.build_ui()
        self.connect_functions()

    def showEvent(self, event):
        self.fill_stages()

    def fill_stages(self):
        self.stages_comboBox.clear()
        stages_list = assets_vars._all_stages_
        for stage in stages_list:
            icon = ressources._stage_icons_dic_[stage]
            self.stages_comboBox.addItem(QtGui.QIcon(icon), stage)

    def add_software_row(self, software, extensions_list, extension_row):
        software_icon = QtWidgets.QLabel()
        software_icon.setPixmap(QtGui.QIcon(ressources._softwares_icons_dic_[software]).pixmap(18))
        software_label = QtWidgets.QLabel(software)

        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QHBoxLayout()
        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(4)
        info_widget.setLayout(info_layout)
        info_layout.addWidget(software_icon)
        info_layout.addWidget(software_label)

        comboBox = extension_comboBox(extension_row)
        comboBox.setFixedWidth(150)
        self.software_rows_layout.addRow(info_widget, comboBox)
        self.combobox_list.append(comboBox)
        comboBox.addItems(extensions_list)
        comboBox.setCurrentText(extension_row['extension'])

    def connect_functions(self):
        self.stages_comboBox.currentTextChanged.connect(self.stage_changed)
        self.apply_button.clicked.connect(self.apply)

    def stage_changed(self):
        self.combobox_list = []
        self.clear_softwares_rows_layout()
        stage = self.stages_comboBox.currentText()
        if stage is not None and stage != '':
            available_softwares = list(assets_vars._ext_dic_[stage].keys())
            for software in available_softwares:
                extensions_list = assets_vars._ext_dic_[stage][software]
                software_id = project.get_software_data_by_name(software, 'id')
                self.add_software_row(software, extensions_list, project.get_default_extension_row(stage, software_id))

    def clear_softwares_rows_layout(self):
        while self.software_rows_layout.rowCount():
            self.software_rows_layout.removeRow(0)

    def refresh(self):
        if self.isVisible():
            self.stage_changed()

    def build_ui(self):
        self.container_layout = QtWidgets.QVBoxLayout()
        self.container_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.container_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(24,24,24,24)
        self.main_layout.setSpacing(12)
        self.main_widget.setLayout(self.main_layout)
        self.container_layout.addWidget(self.main_widget)

        self.title = QtWidgets.QLabel('Exports')
        self.title.setObjectName('title_label')
        self.main_layout.addWidget(self.title)

        self.main_layout.addWidget(gui_utils.separator())

        self.stages_comboBox = gui_utils.QComboBox()
        self.stages_comboBox.setFixedWidth(200)
        self.main_layout.addWidget(self.stages_comboBox)

        self.software_rows_widget = QtWidgets.QWidget()
        self.software_rows_layout = QtWidgets.QFormLayout()
        self.software_rows_layout.setContentsMargins(0,0,0,0)
        self.software_rows_layout.setSpacing(12)
        self.software_rows_widget.setLayout(self.software_rows_layout)
        self.main_layout.addWidget(self.software_rows_widget)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.apply_button = QtWidgets.QPushButton('Apply')
        self.apply_button.setObjectName('blue_button')
        self.apply_button.setDefault(True)
        self.apply_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.apply_button)

    def apply(self):
        stage = self.stages_comboBox.currentText()
        for comboBox in self.combobox_list:
            extension_row = comboBox.extension_row
            extension = comboBox.currentText()
            project.set_default_extension(extension_row['id'], extension)

        self.refresh()

class extension_comboBox(gui_utils.QComboBox):

    def __init__(self, extension_row, parent=None):
        super(extension_comboBox, self).__init__(parent)
        self.extension_row = extension_row
